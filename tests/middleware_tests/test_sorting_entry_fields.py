import pytest

from bibtexparser import Library
from bibtexparser.middlewares.sorting_entry_fields import SortFieldsAlphabeticallyMiddleware, SortFieldsCustomMiddleware
from bibtexparser.model import Entry, Field

TEST_ENTRY = Entry(
    "article",
    "Cesar2013",
    [
        Field("author", "Cesar, J.", 1),
        Field("title", "A title", 2),
        Field("note", "A note", 3),
        Field("journal", "A journal", 3),
        Field("year", "2013", 4),
    ],
)


@pytest.mark.parametrize("inplace", [True, False])
def test_sort_alphabetically(inplace: bool):
    library = Library(blocks=[TEST_ENTRY])
    transformed = SortFieldsAlphabeticallyMiddleware(allow_inplace_modification=inplace).transform(library)
    entry = transformed.entries[0]
    assert entry.fields[0].key == "author"
    assert entry.fields[1].key == "journal"
    assert entry.fields[2].key == "note"
    assert entry.fields[3].key == "title"
    assert entry.fields[4].key == "year"

    # Sanity Checks against unintended external effects
    assert len(transformed.blocks) == 1
    if inplace:
        assert entry is TEST_ENTRY
    else:
        assert entry is not TEST_ENTRY


@pytest.mark.parametrize("inplace", [True, False])
def test_sort_custom_order_case_insensitive(inplace: bool):
    custom_order = ("author", "yEar", "title", "Journal")  # assess case insensitive

    library = Library(blocks=[TEST_ENTRY])
    # case insensitivity is default
    transformed = SortFieldsCustomMiddleware(order=custom_order, allow_inplace_modification=inplace).transform(library)
    entry = transformed.entries[0]
    assert entry.fields[0].key == "author"
    assert entry.fields[1].key == "year"
    assert entry.fields[2].key == "title"
    assert entry.fields[3].key == "journal"
    assert entry.fields[4].key == "note"  # Unspecified fields are appended

    # Sanity Checks against unintended external effects
    assert len(transformed.blocks) == 1
    if inplace:
        assert entry is TEST_ENTRY
    else:
        assert entry is not TEST_ENTRY


def test_sort_order_custom_case_sensitive():
    custom_order = ("author", "yEar", "title", "Journal")  # assess case sensitive

    library = Library(blocks=[TEST_ENTRY])
    transformed = SortFieldsCustomMiddleware(order=custom_order, case_sensitive=True).transform(library)
    entry = transformed.entries[0]
    assert entry.fields[0].key == "author"
    assert entry.fields[1].key == "title"
    assert entry.fields[2].key == "year"  # Unspecified fields (due to case sensitivity) are appended
    assert entry.fields[3].key == "journal"  # Unspecified fields (due to case sensitivity) are appended
    assert entry.fields[4].key == "note"  # Unspecified fields are appended

    assert len(transformed.blocks) == 1