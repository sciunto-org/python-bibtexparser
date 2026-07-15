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


def get_dummy_string():
    return String(key="duplicateKey", value='"A value"')


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


def test_add_string_fails_on_duplicate_by_default():
    """Strict duplicate handling applies to string blocks as well as entries."""
    library = Library(blocks=[get_dummy_string()])

    with pytest.raises(ValueError, match="duplicateKey"):
        library.add(get_dummy_string())

    assert len(library.strings) == 1
    assert len(library.failed_blocks) == 0


def test_entry_and_string_keys_use_separate_namespaces():
    """An entry and string may share a key without becoming duplicate blocks."""
    library = Library(blocks=[get_dummy_entry(), get_dummy_string()])

    assert len(library.entries) == 1
    assert len(library.strings) == 1
    assert len(library.failed_blocks) == 0


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
