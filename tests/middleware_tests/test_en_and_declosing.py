from copy import deepcopy
from typing import Union

import pytest

from bibtexparser.library import Library
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware, AddEnclosingMiddleware
from bibtexparser.model import String, Entry, Field, Block, Preamble, ImplicitComment, ExplicitComment
from tests.resources import ENCLOSINGS, EDGE_CASE_VALUES


def _skip_pseudo_enclosing_value(value: str):
    starts_and_ends_in_brackets = value.startswith("{") and value.endswith("}")
    starts_and_ends_in_quotes = value.startswith('"') and value.endswith('"')
    if starts_and_ends_in_quotes or starts_and_ends_in_brackets:
        pytest.skip("No enclosing to remove")


@pytest.mark.parametrize("enclosing", ENCLOSINGS +
                         [pytest.param("{0}", id="no_enclosing")])
@pytest.mark.parametrize("value", EDGE_CASE_VALUES)
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_removal_of_enclosing_on_string(enclosing, value, inplace):
    """Extensive Matrix-Testing of the RemoveEnclosingMiddleware on Strings.

    Also covers the internals for other block types (i.e., Entry),
    which thus can be tested more light-weight."""

    if enclosing == "{0}":
        _skip_pseudo_enclosing_value(value)

    # Create test string
    key = "someKey"
    raw = f"<--- does not matter for this unit test -->"
    start_line = 5

    original = String(start_line=start_line,
                      key=key,
                      raw=raw,
                      value=enclosing.format(value))

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=inplace)

    transformed_library = middleware.transform(library=Library([original]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.strings) == 1
    # Assert correct removal of enclosing
    transformed = transformed_library.strings[0]
    assert transformed.value == value
    expected_enclosing = enclosing.format("")[0] if enclosing != "{0}" else "no-enclosing"
    assert transformed.parser_metadata["removed_enclosing"] == expected_enclosing
    # Assert remaining fields are unchanged
    assert transformed.start_line == start_line
    assert transformed.key == key
    assert transformed.raw == raw

    # Assert inplace modification
    if inplace:
        # Note that this is not a strict requirement,
        #   as "allow_inplace" does not mandate inplace modification,
        #   but it should be implemented as such for this middleware
        #   for performance reasons.
        assert transformed is original
    else:
        assert transformed is not original


@pytest.mark.parametrize("enclosing", ENCLOSINGS)
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_removal_of_enclosing_on_entry(enclosing: str, inplace: bool):
    """Test the RemoveEnclosingMiddleware on Entries."""

    fields = {
        # Enclosed string value
        "author": Field(value=enclosing.format("Michael Weiss"), start_line=6, key="year"),
        # Unenclosed int value
        "year": Field(value="2019", start_line=7, key="year"),
        # Enclosed int value
        "month": Field(value=enclosing.format("1"), start_line=8, key="month"),
    }

    input_entry = Entry(start_line=5,
                        entry_type="article",
                        raw="<--- does not matter for this unit test -->",
                        key="someKey",
                        fields=fields)

    input_entry_copy = deepcopy(input_entry)

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=inplace)
    transformed_library = middleware.transform(library=Library([input_entry]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.entries) == 1
    # Assert fields are transformed correctly
    transformed_fields = transformed_library.entries[0].fields
    assert transformed_fields["author"].value == "Michael Weiss"
    assert transformed_fields["year"].value == "2019"
    assert transformed_fields["month"].value == "1"

    # Assert remaining fields are unchanged
    assert transformed_library.entries[0].start_line == input_entry_copy.start_line
    assert transformed_library.entries[0].entry_type == input_entry_copy.entry_type
    assert transformed_library.entries[0].raw == input_entry_copy.raw
    assert transformed_library.entries[0].key == input_entry_copy.key


@pytest.mark.parametrize("block", [
    pytest.param(
        Preamble(start_line=5, raw="@Preamble{a_x + b_x^2}", value="a_x + b_x^2"),
        id="preamble"
    ),
    pytest.param(
        ImplicitComment(start_line=5, raw="# MyComment", comment="MyComment"),
        id="implicit_comment"
    ),
    pytest.param(
        ExplicitComment(start_line=5, raw="@Comment{MyComment}", comment="MyComment"),
        id="explicit_comment"
    ),
])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_unimpacted_block_types_remain_unchanged(block: Block,
                                                 inplace: bool):
    # TODO this can probably be extracted in a test-utils class,
    #   as almost every middleware will have a test like that.
    input_copy = deepcopy(block)
    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=inplace)
    transformed_library = middleware.transform(library=Library([block]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert transformed_library.blocks[0] == input_copy
    if inplace:
        # Note that this is not a strict requirement,
        #   as "allow_inplace" does not mandate inplace modification,
        #   but it should be implemented as such for this middleware
        #   for performance reasons.
        assert transformed_library.blocks[0] is block
    else:
        assert transformed_library.blocks[0] is not block


@pytest.mark.parametrize("metadata_enclosing", ["{", '"', "no-enclosing", None])
@pytest.mark.parametrize("default_enclosing", ["{", '"', "no-enclosing"])
@pytest.mark.parametrize("enclose_ints", [True, False], ids=["enclose_ints", "no_enclose_ints"])
@pytest.mark.parametrize("reuse_previous_enclosing", [True, False], ids=["reuse", "no_reuse"])
@pytest.mark.parametrize("value", EDGE_CASE_VALUES + ["1990"])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_addition_of_enclosing_on_entry(metadata_enclosing: str,
                                        default_enclosing: str,
                                        enclose_ints: bool,
                                        reuse_previous_enclosing: bool,
                                        value: Union[str, int],
                                        inplace: bool):
    """Extensive Matrix-Testing of the AddEnclosingMiddleware on Entries.

    Also covers the internals for other block types (i.e., String),
    which thus can be tested more light-weight."""
    # These values not matter for this unit test, 
    #   but must not change during transformation
    #   (hence, they are created as variables, not directly in Entry constructor)
    input_entry = Entry(start_line=5,
                        entry_type="article",
                        raw="<--- does not matter for this unit test -->",
                        key="someKey",
                        fields={"year": Field(value=value,
                                              start_line=6,
                                              key="year")})
    input_entry_copy = deepcopy(input_entry)

    if metadata_enclosing is not None:
        input_entry.parser_metadata["removed_enclosing"] = {
            "year": metadata_enclosing
        }

    middleware = AddEnclosingMiddleware(allow_inplace_modification=inplace,
                                        default_enclosing=default_enclosing,
                                        reuse_previous_enclosing=reuse_previous_enclosing,
                                        enclose_integers=enclose_ints)

    transformed_library = middleware.transform(library=Library([input_entry]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.entries) == 1
    # Assert correct addition of enclosing
    transformed = transformed_library.entries[0]
    changed_value = transformed.fields["year"].value

    # Figure out which enclosing was added
    if changed_value.startswith('"') and changed_value.endswith('"'):
        used_enclosing = '"'
    elif changed_value.startswith('{') and changed_value.endswith('}'):
        used_enclosing = '{'
    elif str(changed_value) == str(value):
        used_enclosing = "no-enclosing"
    else:
        raise ValueError(f"Strange encoding: {changed_value}")

    # Assert correct enclosing was added
    if reuse_previous_enclosing and metadata_enclosing is not None:
        expected_enclosing = metadata_enclosing
    elif (isinstance(value, int) or value.isdigit()) and not enclose_ints:
        expected_enclosing = "no-enclosing"
    else:
        expected_enclosing = default_enclosing

    if expected_enclosing == "no-enclosing":
        _skip_pseudo_enclosing_value(value)

    assert used_enclosing == expected_enclosing

    if inplace:
        # Note that this is not a strict requirement,
        #   as "allow_inplace" does not mandate inplace modification,
        #   but it should be implemented as such for this middleware
        #   for performance reasons.
        assert transformed is input_entry
    else:
        assert transformed is not input_entry

# TODO add test to add enclosing for string

# Todo add add-enclosing tests for unimpacted blocks (preamble, comment, etc.)
#   this can mostly be extracted from above.
