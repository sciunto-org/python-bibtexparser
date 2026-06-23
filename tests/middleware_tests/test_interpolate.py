import pytest

import bibtexparser
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.interpolate import ResolveStringReferencesMiddleware
from bibtexparser.splitter import Splitter

bibtex_string = """
@string{test_note = "This is a test note."}

@article{test_article,
  author  = "Smith, John",
  title   = "A Test Article",
  journal = "Journal of Testing",
  year    = "2022",
  note    = test_note
}

"""


def test_string_interpolation_middleware_interpolates_string():
    original_lib = Splitter(bibtex_string).split()

    # Prerequisite
    assert original_lib.entries_dict["test_article"].fields_dict["note"].value == "test_note"

    # Apply middleware
    m = ResolveStringReferencesMiddleware(allow_inplace_modification=False)
    changed_library = m.transform(original_lib)

    assert original_lib is not changed_library
    assert (
        changed_library.entries_dict["test_article"].fields_dict["note"].value
        == '"This is a test note."'
    )


def test_string_interpolation_is_case_insensitive():
    bibtex = """
    @string{lowercase = "Lower Case Note."}
    @string{UPPERCASE = "Upper Case Note."}

    @article{test_article,
      note    = LOWERCASE,
      comment = uppercase
    }
    """
    library = Splitter(bibtex).split()

    m = ResolveStringReferencesMiddleware()
    library = m.transform(library)

    fields = library.entries_dict["test_article"].fields_dict
    assert fields["note"].value == '"Lower Case Note."'
    assert fields["comment"].value == '"Upper Case Note."'


def test_warning_is_raised_if_enclosings_are_removed():
    original_lib = Splitter(bibtex_string).split()
    m = RemoveEnclosingMiddleware(allow_inplace_modification=False)
    no_enclosing_library = m.transform(original_lib)

    with pytest.warns(UserWarning) as record:
        m = ResolveStringReferencesMiddleware(allow_inplace_modification=False)
        m.transform(no_enclosing_library)

    assert len(record) == 1
    assert "RemoveEnclosing" in record[0].message.args[0]


def test_string_interpolation_resolves_concatenation():
    bibtex = """
    @string{jan = "Jan."}

    @inbook{test_inbook,
      month   = 10 # "~" # jan,
      title   = "hello" # " " # "world",
      mixed   = jan # {  } # "X",
      numbers = 1 # 2 # 3
    }
    """
    library = Splitter(bibtex).split()

    m = ResolveStringReferencesMiddleware()
    library = m.transform(library)

    fields = library.entries_dict["test_inbook"].fields_dict
    # Concatenations are resolved and kept enclosed in braces.
    assert fields["month"].value == "{10~Jan.}"
    assert fields["title"].value == "{hello world}"
    assert fields["mixed"].value == "{Jan.  X}"
    assert fields["numbers"].value == "{123}"


def test_string_interpolation_leaves_unresolvable_concatenation_untouched():
    bibtex = """
    @inbook{test_inbook,
      note = unknown_macro # " suffix"
    }
    """
    library = Splitter(bibtex).split()

    m = ResolveStringReferencesMiddleware()
    library = m.transform(library)

    # An unknown reference means the expression is left exactly as-is.
    assert (
        library.entries_dict["test_inbook"].fields_dict["note"].value == 'unknown_macro # " suffix"'
    )


def test_parse_string_resolves_concatenation_end_to_end():
    # Exact reproduction of issue #396.
    bibtex_str = """
    @STRING{ jan = "Jan." }

    @INBOOK{inbook-full,
       month = 10 # "~" # jan,
    }
    """
    library = bibtexparser.parse_string(bibtex_str)
    month = library.entries[0].fields_dict["month"].value
    assert month == "10~Jan."

    # The resolved value writes as a valid, brace-enclosed string and
    # round-trips back to the same value.
    written = bibtexparser.write_string(library)
    assert "month = {10~Jan.}" in written
    reparsed = bibtexparser.parse_string(written)
    assert reparsed.entries[0].fields_dict["month"].value == "10~Jan."
