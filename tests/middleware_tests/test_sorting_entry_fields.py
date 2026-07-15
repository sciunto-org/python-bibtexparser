import pytest

from bibtexparser import Library
from bibtexparser import write_string
from bibtexparser.middlewares.sorting_entry_fields import SortFieldsAlphabeticallyMiddleware
from bibtexparser.middlewares.sorting_entry_fields import SortFieldsCustomMiddleware
from bibtexparser.model import Entry
from bibtexparser.model import Field


def _test_entry():
    """Return a fresh entry so in-place middleware tests cannot affect each other."""
    return Entry(
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
    original_entry = _test_entry()
    library = Library(blocks=[original_entry])
    m = SortFieldsAlphabeticallyMiddleware(allow_inplace_modification=inplace)
    transformed = m.transform(library)
    entry = transformed.entries[0]
    assert entry.fields[0].key == "author"
    assert entry.fields[1].key == "journal"
    assert entry.fields[2].key == "note"
    assert entry.fields[3].key == "title"
    assert entry.fields[4].key == "year"

    # Sanity Checks against unintended external effects
    assert len(transformed.blocks) == 1
    if inplace:
        assert entry is original_entry
    else:
        assert entry is not original_entry


@pytest.mark.parametrize("inplace", [True, False])
def test_sort_custom_order_case_insensitive(inplace: bool):
    custom_order = ("author", "yEar", "title", "Journal")  # assess case insensitive

    original_entry = _test_entry()
    library = Library(blocks=[original_entry])
    # case insensitivity is default
    m = SortFieldsCustomMiddleware(order=custom_order, allow_inplace_modification=inplace)
    transformed = m.transform(library)
    entry = transformed.entries[0]
    assert entry.fields[0].key == "author"
    assert entry.fields[1].key == "year"
    assert entry.fields[2].key == "title"
    assert entry.fields[3].key == "journal"
    assert entry.fields[4].key == "note"  # Unspecified fields are appended

    # Sanity Checks against unintended external effects
    assert len(transformed.blocks) == 1
    if inplace:
        assert entry is original_entry
    else:
        assert entry is not original_entry


def test_sort_order_custom_case_sensitive():
    custom_order = ("author", "yEar", "title", "Journal")  # assess case sensitive

    library = Library(blocks=[_test_entry()])
    m = SortFieldsCustomMiddleware(order=custom_order, case_sensitive=True)
    transformed = m.transform(library)
    entry = transformed.entries[0]
    assert entry.fields[0].key == "author"
    assert entry.fields[1].key == "title"

    # Unspecified fields are appended in their original relative order.
    assert entry.fields[2].key == "note"
    assert entry.fields[3].key == "journal"
    assert entry.fields[4].key == "year"

    assert len(transformed.blocks) == 1


def test_custom_order_applies_during_public_write():
    """The public writer applies custom ordering without mutating the source library."""
    original_entry = _test_entry()
    library = Library(blocks=[original_entry])
    middleware = SortFieldsCustomMiddleware(
        order=("year", "author"), allow_inplace_modification=False
    )

    written = write_string(library, prepend_middleware=[middleware])
    written_field_keys = [
        line.split("=", maxsplit=1)[0].strip() for line in written.splitlines() if "=" in line
    ]

    assert written_field_keys == ["year", "author", "title", "note", "journal"]
    assert [field.key for field in original_entry.fields] == [
        "author",
        "title",
        "note",
        "journal",
        "year",
    ]


@pytest.mark.parametrize(
    "order",
    [
        pytest.param(("title", "title"), id="identical"),
        pytest.param(("title", "TITLE"), id="case-insensitive"),
    ],
)
def test_custom_order_rejects_duplicate_keys(order):
    """Ambiguous custom orders fail early, including case-only duplicates by default."""
    with pytest.raises(ValueError, match="title"):
        SortFieldsCustomMiddleware(order=order)
