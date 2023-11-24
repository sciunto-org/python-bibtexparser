from copy import deepcopy

import pytest

from bibtexparser import Library
from bibtexparser.model import Entry, Field


def get_dummy_entry():
    return Entry(
        entry_type="article",
        key="duplicateKey",
        fields=[
            Field(key="title", value="A title"),
            Field(key="author", value="An author"),
        ],
    )


def test_replace_with_duplicates():
    """Test that replace() works when there are duplicate values. See issue 404."""
    library = Library()
    library.add(get_dummy_entry())
    library.add(get_dummy_entry())
    # Test precondition
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1

    replacement_entry = get_dummy_entry()
    replacement_entry.fields_dict["title"].value = "A new title"

    library.replace(
        library.failed_blocks[0], replacement_entry, fail_on_duplicate_key=False
    )
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1
    assert library.failed_blocks[0].ignore_error_block["title"] == "A new title"

    replacement_entry_2 = get_dummy_entry()
    replacement_entry_2.fields_dict["title"].value = "Another new title"

    library.replace(
        library.entries[0], replacement_entry_2, fail_on_duplicate_key=False
    )
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1
    # The new block replaces the previous "non-duplicate" and should thus not become a duplicate itself
    assert library.entries[0].fields_dict["title"].value == "Another new title"


def test_replace_fail_on_duplicate():
    library = Library()
    replaceable_entry = get_dummy_entry()
    replaceable_entry.key = "Just a regular entry, to be replaced"
    future_duplicate_entry = get_dummy_entry()
    library.add([replaceable_entry, future_duplicate_entry])

    with pytest.raises(ValueError):
        library.replace(
            replaceable_entry, get_dummy_entry(), fail_on_duplicate_key=True
        )

    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 0
    assert library.entries[0].key == "Just a regular entry, to be replaced"
    assert library.entries[1].key == "duplicateKey"


def test_fail_on_duplicate_add():
    library = Library()
    library.add(get_dummy_entry())
    with pytest.raises(ValueError):
        library.add(get_dummy_entry(), fail_on_duplicate_key=True)
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1
