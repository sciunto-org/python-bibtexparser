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


def test_string_interpolation_resolves_string_definitions_recursively():
    """A definition may itself be an expression or another reference (cases via @claell)."""
    bibtex = """
    @string{asiacryptname = "Asiacrypt"}
    @string{asiacrypt91name = asiacryptname # "'91"}
    @string{alias = asiacrypt91name}
    @string{quoted = "Asia" # "crypt"}
    @string{vol = 1 # 0}

    @inbook{test_inbook,
      booktitle = asiacrypt91name,
      series    = alias,
      note      = asiacrypt91name # " proceedings",
      title     = quoted,
      volume    = vol
    }
    """
    library = bibtexparser.parse_string(bibtex)

    fields = library.entries_dict["test_inbook"].fields_dict
    assert fields["booktitle"].value == "Asiacrypt'91"
    assert fields["series"].value == "Asiacrypt'91"
    assert fields["note"].value == "Asiacrypt'91 proceedings"
    assert fields["title"].value == "Asiacrypt"
    assert fields["volume"].value == "10"

    # The definitions keep their expression form, so the file still writes validly.
    written = bibtexparser.write_string(library)
    assert 'asiacrypt91name = asiacryptname # "\'91"' in written
    assert 'quoted = "Asia" # "crypt"' in written


def test_string_interpolation_leaves_cyclic_definitions_unresolved():
    """Cyclic definitions resolve to nothing rather than to a partial value (case via @claell)."""
    bibtex = """
    @string{first = second # " one"}
    @string{second = first # " two"}
    @string{itself = itself}

    @inbook{test_inbook,
      title = first # "!",
      note  = second,
      other = itself
    }
    """
    library = bibtexparser.parse_string(bibtex)

    fields = library.entries_dict["test_inbook"].fields_dict
    assert fields["title"].value == 'first # "!"'
    assert fields["note"].value == "second"
    assert fields["other"].value == "itself"

    # Writing and re-parsing is a fixpoint, i.e. it does not substitute one more level.
    written = bibtexparser.write_string(library)
    reparsed = bibtexparser.parse_string(written).entries_dict["test_inbook"].fields_dict
    assert reparsed["title"].value == 'first # "!"'
    assert reparsed["note"].value == "second"
    assert reparsed["other"].value == "itself"


def test_string_interpolation_resolves_long_definition_chains():
    """A chain of definitions is resolved iteratively, so it cannot exhaust the stack."""
    length = 500
    bibtex = "".join(f'@string{{s{i} = s{i + 1} # "x"}}\n' for i in range(length))
    bibtex += f'@string{{s{length} = "end"}}\n@inbook{{test_inbook, title = s0}}'

    library = bibtexparser.parse_string(bibtex)

    title = library.entries_dict["test_inbook"].fields_dict["title"]
    assert title.value == "end" + "x" * length


def test_unresolvable_concatenation_survives_a_round_trip():
    """An expression with an unknown reference is written back exactly as it was read."""
    bibtex = (
        "@inbook{test_inbook,\n"
        '  note = "prefix" # unknown_macro # "suffix",\n'
        "  title = {first} # unknown_macro # {second}\n"
        "}"
    )
    library = bibtexparser.parse_string(bibtex)

    fields = library.entries_dict["test_inbook"].fields_dict
    assert fields["note"].value == '"prefix" # unknown_macro # "suffix"'
    assert fields["title"].value == "{first} # unknown_macro # {second}"

    written = bibtexparser.write_string(library)
    assert 'note = "prefix" # unknown_macro # "suffix"' in written
    assert "title = {first} # unknown_macro # {second}" in written
    reparsed = bibtexparser.parse_string(written).entries_dict["test_inbook"].fields_dict
    assert reparsed["note"].value == fields["note"].value
    assert reparsed["title"].value == fields["title"].value
