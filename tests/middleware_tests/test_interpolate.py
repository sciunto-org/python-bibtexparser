import pytest

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
