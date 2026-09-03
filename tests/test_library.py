import pytest

from bibtexparser import Library
from bibtexparser.model import Entry
from bibtexparser.model import Field
from bibtexparser.model import ImplicitComment
from bibtexparser.model import String


def get_dummy_entry():
    return Entry(
        entry_type="article",
        key="duplicateKey",
        fields=[
            Field(key="title", value="A title"),
            Field(key="author", value="An author"),
        ],
    )


def get_dummy_entry_with_key(key: str):
    entry = get_dummy_entry()
    entry.key = key
    return entry


def test_replace_with_duplicates():
    """Test that replace() works when there are duplicate values. See issue 404."""
    library = Library()
    library.add(get_dummy_entry())
    library.add(get_dummy_entry(), fail_on_duplicate_key=False)
    # Test precondition
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1

    replacement_entry = get_dummy_entry()
    replacement_entry.fields_dict["title"].value = "A new title"

    library.replace(library.failed_blocks[0], replacement_entry, fail_on_duplicate_key=False)
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1
    assert library.failed_blocks[0].ignore_error_block["title"] == "A new title"

    replacement_entry_2 = get_dummy_entry()
    replacement_entry_2.fields_dict["title"].value = "Another new title"

    library.replace(library.entries[0], replacement_entry_2, fail_on_duplicate_key=False)
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
        library.replace(replaceable_entry, get_dummy_entry(), fail_on_duplicate_key=True)

    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 0
    assert library.entries[0].key == "Just a regular entry, to be replaced"
    assert library.entries[1].key == "duplicateKey"


def test_add_fails_on_duplicate_by_default():
    library = Library()
    library.add(get_dummy_entry())
    with pytest.raises(ValueError):
        library.add(get_dummy_entry())
    # The failed add must leave the library unchanged.
    assert len(library.blocks) == 1
    assert len(library.failed_blocks) == 0


def test_add_with_duplicates_in_same_call_fails_atomically():
    unique_entry = get_dummy_entry()
    unique_entry.key = "uniqueKey"
    library = Library()
    with pytest.raises(ValueError):
        library.add([unique_entry, get_dummy_entry(), get_dummy_entry()])
    # Not even the non-duplicate blocks of the failed call are added.
    assert len(library.blocks) == 0


def test_add_duplicate_does_not_fail_if_disabled():
    library = Library()
    library.add(get_dummy_entry())
    library.add(get_dummy_entry(), fail_on_duplicate_key=False)
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1


def test_constructor_fails_on_duplicate_by_default():
    with pytest.raises(ValueError):
        Library(blocks=[get_dummy_entry(), get_dummy_entry()])

    library = Library(blocks=[get_dummy_entry(), get_dummy_entry()], fail_on_duplicate_key=False)
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 1


def test_remove_prefers_identical_instance_over_equal_block():
    """With two equal blocks, remove() must remove the passed instance. See issue 537."""
    first_comment = ImplicitComment("#same")
    second_comment = ImplicitComment("#same")
    assert first_comment == second_comment

    library = Library()
    library.add([first_comment, second_comment])

    library.remove(second_comment)
    assert len(library.blocks) == 1
    assert library.blocks[0] is first_comment


def test_replace_prefers_identical_instance_over_equal_block():
    """With two equal blocks, replace() must replace the passed instance. See issue 537."""
    first_comment = ImplicitComment("#same")
    second_comment = ImplicitComment("#same")
    assert first_comment == second_comment

    library = Library()
    library.add([first_comment, second_comment])

    new_comment = ImplicitComment("#new")
    library.replace(second_comment, new_comment)
    assert len(library.blocks) == 2
    assert library.blocks[0] is first_comment
    assert library.blocks[1] is new_comment


def test_remove_entry_with_changed_key():
    """Removing an entry whose key changed after adding must not fail. See issue 565."""
    library = Library()
    entry = get_dummy_entry()
    other_entry = get_dummy_entry()
    other_entry.key = "otherKey"
    library.add([entry, other_entry])

    entry.key = "changedKey"
    library.remove(entry)

    assert library.blocks == [other_entry]
    assert library.entries == [other_entry]
    assert library.entries_dict == {"otherKey": other_entry}
    library.add(get_dummy_entry())
    assert len(library.blocks) == 2
    assert len(library.failed_blocks) == 0


def test_remove_string_with_changed_key():
    """Removing a string whose key changed after adding must not fail."""
    library = Library()
    string = String(key="someString", value='"some value"')
    other_string = String(key="otherString", value='"other value"')
    library.add([string, other_string])

    string.key = "changedKey"
    library.remove(string)

    assert library.blocks == [other_string]
    assert library.strings == [other_string]
    assert library.strings_dict == {"otherString": other_string}


def test_remove_block_not_in_library_raises_value_error():
    library = Library()
    entry = get_dummy_entry()
    library.add(entry)

    with pytest.raises(ValueError):
        library.remove(get_dummy_entry_with_key("notInLibrary"))

    assert library.blocks == [entry]
    assert library.entries_dict == {"duplicateKey": entry}


def test_remove_list_with_missing_block_is_atomic():
    """If one block of a removed list is missing, no block is removed."""
    library = Library()
    entry = get_dummy_entry()
    library.add(entry)

    with pytest.raises(ValueError):
        library.remove([entry, get_dummy_entry_with_key("notInLibrary")])

    assert library.blocks == [entry]
    assert library.entries == [entry]
    assert library.entries_dict == {"duplicateKey": entry}


def test_remove_list_of_blocks():
    library = Library()
    entries = [get_dummy_entry_with_key(f"key{i}") for i in range(3)]
    library.add(entries)

    library.remove([entries[0], entries[2]])

    assert library.blocks == [entries[1]]
    assert library.entries_dict == {"key1": entries[1]}


def test_replace_entry_with_changed_key():
    """Replacing an entry whose key changed after adding must not fail. See issue 565."""
    library = Library()
    entry = get_dummy_entry()
    library.add(entry)
    entry.key = "changedKey"

    replacement = get_dummy_entry_with_key("replacementKey")
    library.replace(entry, replacement)

    assert library.blocks == [replacement]
    assert library.entries == [replacement]
    assert library.entries_dict == {"replacementKey": replacement}


class _NonIterableDict(dict):
    """A dict that supports lookups but refuses to be iterated or copied.

    Used to make sure that `Library.add` does not walk the whole by-key dicts
    (i.e., does not scale with the library size) when checking for duplicates."""

    def __iter__(self):
        raise AssertionError("by-key dict must not be iterated on add")

    def keys(self):
        raise AssertionError("by-key dict must not be iterated on add")


def test_add_duplicate_check_does_not_iterate_library():
    """Checking for duplicates must not iterate over all existing keys (was O(library size))."""
    library = Library()
    library.add([get_dummy_entry_with_key("existing"), String(key="s", value="{v}")])
    library._entries_by_key = _NonIterableDict(library._entries_by_key)
    library._strings_by_key = _NonIterableDict(library._strings_by_key)

    library.add(ImplicitComment(comment="a comment"))
    library.add(get_dummy_entry_with_key("new"))
    library.add(String(key="t", value="{w}"))
    assert len(library.blocks) == 5

    with pytest.raises(ValueError):
        library.add(get_dummy_entry_with_key("existing"))
    with pytest.raises(ValueError):
        library.add(String(key="s", value="{v}"))
    with pytest.raises(ValueError):
        library.add([get_dummy_entry_with_key("twice"), get_dummy_entry_with_key("twice")])
    assert len(library.blocks) == 5
