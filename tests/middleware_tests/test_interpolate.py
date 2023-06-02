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
    original_library = Splitter(bibtex_string).split()

    # Prerequisite
    assert (
        original_library.entries_dict["test_article"].fields_dict["note"].value
        == "test_note"
    )

    # Apply middleware
    changed_library = ResolveStringReferencesMiddleware(
        allow_inplace_modification=False
    ).transform(original_library)

    assert original_library is not changed_library
    assert (
        changed_library.entries_dict["test_article"].fields_dict["note"].value
        == '"This is a test note."'
    )


def test_warning_is_raised_if_enclosings_are_removed():
    original_library = Splitter(bibtex_string).split()
    no_enclosing_library = RemoveEnclosingMiddleware(
        allow_inplace_modification=False
    ).transform(original_library)

    with pytest.warns(UserWarning) as record:
        ResolveStringReferencesMiddleware(allow_inplace_modification=False).transform(
            no_enclosing_library
        )

    assert len(record) == 1
    assert "RemoveEnclosing" in record[0].message.args[0]
