from copy import deepcopy
from typing import Union

import pytest

from bibtexparser.library import Library
from bibtexparser.middlewares.enclosing import AddEnclosingMiddleware
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.model import Entry
from bibtexparser.model import Field
from bibtexparser.model import String
from tests.middleware_tests.middleware_test_util import assert_block_does_not_change
from tests.middleware_tests.middleware_test_util import assert_inplace_is_respected
from tests.middleware_tests.middleware_test_util import assert_nonfield_entry_attributes_unchanged
from tests.resources import EDGE_CASE_VALUES
from tests.resources import ENCLOSINGS


def _skip_pseudo_enclosing_value(value: str):
    starts_and_ends_in_brackets = value.startswith("{") and value.endswith("}")
    starts_and_ends_in_quotes = value.startswith('"') and value.endswith('"')
    if starts_and_ends_in_quotes or starts_and_ends_in_brackets:
        pytest.skip("No enclosing to remove")


@pytest.mark.parametrize("enclosing", ENCLOSINGS + [pytest.param("{0}", id="no_enclosing")])
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
    raw = "<--- does not matter for this unit test -->"
    start_line = 5

    original = String(start_line=start_line, key=key, raw=raw, value=enclosing.format(value))

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

    # Assert `allow_inplace_modification` is respected
    assert_inplace_is_respected(inplace, original, transformed)


@pytest.mark.parametrize("enclosing", ENCLOSINGS)
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_removal_of_enclosing_on_entry(enclosing: str, inplace: bool):
    """Test the RemoveEnclosingMiddleware on Entries."""

    fields = [
        # Enclosed string value
        Field(value=enclosing.format("Michael Weiss"), start_line=6, key="author"),
        # Unenclosed int value
        Field(value="2019", start_line=7, key="year"),
        # Enclosed int value
        Field(value=enclosing.format("1"), start_line=8, key="month"),
    ]

    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=fields,
    )

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=inplace)
    transformed_library = middleware.transform(library=Library([input_entry]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.entries) == 1
    # Assert fields are transformed correctly
    transformed_fields = transformed_library.entries[0].fields_dict
    assert transformed_fields["author"].value == "Michael Weiss"
    assert transformed_fields["year"].value == "2019"
    assert transformed_fields["month"].value == "1"

    # Assert remaining fields are unchanged
    assert_nonfield_entry_attributes_unchanged(input_entry, transformed_library.entries[0])

    # Assert `allow_inplace_modification` is respected
    assert_inplace_is_respected(inplace, input_entry, transformed_library.entries[0])


@pytest.mark.parametrize("block", ["preamble", "implicit_comment", "explicit_comment"])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_no_removal_blocktypes(block: str, inplace: bool):
    assert_block_does_not_change(
        block_type=block,
        middleware=RemoveEnclosingMiddleware(allow_inplace_modification=inplace),
        same_instance=inplace,
    )


@pytest.mark.parametrize("metadata_enclosing", ["{", '"', "no-enclosing", None])
@pytest.mark.parametrize("default_enclosing", ["{", '"'])
@pytest.mark.parametrize("enclose_ints", [True, False], ids=["enclose_ints", "no_enclose_ints"])
@pytest.mark.parametrize("reuse_previous_enclosing", [True, False], ids=["reuse", "no_reuse"])
@pytest.mark.parametrize("value", EDGE_CASE_VALUES + ["1990"])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_addition_of_enclosing_on_entry(
    metadata_enclosing: str,
    default_enclosing: str,
    enclose_ints: bool,
    reuse_previous_enclosing: bool,
    value: Union[str, int],
    inplace: bool,
):
    """Extensive Matrix-Testing of the AddEnclosingMiddleware on Entries.

    Also covers the internals for other block types (i.e., String),
    which thus can be tested more light-weight."""
    # These values not matter for this unit test,
    #   but must not change during transformation
    #   (hence, they are created as variables, not directly in Entry constructor)
    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[Field(value=value, start_line=6, key="year")],
    )

    if metadata_enclosing is not None:
        input_entry.parser_metadata["removed_enclosing"] = {"year": metadata_enclosing}

    middleware = AddEnclosingMiddleware(
        allow_inplace_modification=inplace,
        default_enclosing=default_enclosing,
        reuse_previous_enclosing=reuse_previous_enclosing,
        enclose_integers=enclose_ints,
    )

    transformed_library = middleware.transform(library=Library([input_entry]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.entries) == 1
    # Assert correct addition of enclosing
    transformed = transformed_library.entries[0]
    changed_value = transformed["year"]

    # Figure out which enclosing was added
    used_enclosing = _figure_out_added_enclosing(changed_value, value)

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

    # Assert remaining fields are unchanged
    assert_nonfield_entry_attributes_unchanged(input_entry, transformed)

    # Assert `allow_inplace_modification` is respected
    assert_inplace_is_respected(inplace, input_entry, transformed)


def _figure_out_added_enclosing(changed_value, value):
    if changed_value.startswith('"') and changed_value.endswith('"'):
        used_enclosing = '"'
    elif changed_value.startswith("{") and changed_value.endswith("}"):
        used_enclosing = "{"
    elif str(changed_value) == str(value):
        used_enclosing = "no-enclosing"
    else:
        raise ValueError(f"Strange encoding: {changed_value}")
    return used_enclosing


@pytest.mark.parametrize("metadata_resolving", ["", "journal"])
@pytest.mark.parametrize("metadata_enclosing", ["{", '"', "no-enclosing", None])
@pytest.mark.parametrize("default_enclosing", ["{", '"'])
@pytest.mark.parametrize("enclose_ints", [True, False], ids=["enclose_ints", "no_enclose_ints"])
@pytest.mark.parametrize(
    "keep_abbr_string", [True, False], ids=["keep_abbr_string", "no_keep_abbr_string"]
)
@pytest.mark.parametrize("reuse_previous_enclosing", [True, False], ids=["reuse", "no_reuse"])
@pytest.mark.parametrize(
    "value",
    [
        # value, is a abbreviation?
        ("IEEE_T_PAMI", True),
        ('IEEE_T_PAMI # "ieee tpami"', True),
        ('IEEE_T_PAMI" # ieee tpami', False),
        ('IEEE_T-PAMI # "ieee tpami"', False),
        ('IEEE_T-PAMI # "ieee # tpami"', False),
        ('IEEE T-PAMI # "ieee tpami"', False),
    ],
)
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_addition_of_enclosing_on_entry_with_abbr(
    value: tuple,
    metadata_resolving: str,
    keep_abbr_string: bool,
    metadata_enclosing: str,
    default_enclosing: str,
    enclose_ints: bool,
    reuse_previous_enclosing: bool,
    inplace: bool,
):
    """Extensive Matrix-Testing of the AddEnclosingMiddleware on Entries.

    Also covers the internals for other block types (i.e., String),
    which thus can be tested more light-weight."""
    # These values not matter for this unit test,
    #   but must not change during transformation
    #   (hence, they are created as variables, not directly in Entry constructor)
    value, is_abbr = value
    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[Field(value=value, start_line=6, key="journal")],
    )

    if metadata_resolving:
        input_entry.parser_metadata["ResolveStringReferences"] = [metadata_resolving]
    if metadata_enclosing is not None:
        input_entry.parser_metadata["removed_enclosing"] = {"journal": metadata_enclosing}

    middleware = AddEnclosingMiddleware(
        allow_inplace_modification=inplace,
        default_enclosing=default_enclosing,
        reuse_previous_enclosing=reuse_previous_enclosing,
        enclose_integers=enclose_ints,
        keep_abbr_string=keep_abbr_string,
    )

    transformed_library = middleware.transform(library=Library([input_entry]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.entries) == 1
    # Assert correct addition of enclosing
    transformed = transformed_library.entries[0]
    changed_value = transformed["journal"]

    # Assert correct enclosing was added
    if reuse_previous_enclosing and metadata_enclosing is not None:
        expected_enclosing = metadata_enclosing
    elif (isinstance(value, int) or value.isdigit()) and not enclose_ints:
        expected_enclosing = "no-enclosing"
    elif not metadata_resolving and keep_abbr_string:
        if is_abbr:
            expected_enclosing = "no-enclosing"
        else:
            expected_enclosing = default_enclosing
    else:
        expected_enclosing = default_enclosing

    if expected_enclosing == "no-enclosing":
        _skip_pseudo_enclosing_value(value)

    assert changed_value == middleware._enclose_value(value, expected_enclosing)

    # Assert remaining fields are unchanged
    assert_nonfield_entry_attributes_unchanged(input_entry, transformed)

    # Assert `allow_inplace_modification` is respected
    assert_inplace_is_respected(inplace, input_entry, transformed)


@pytest.mark.parametrize("metadata_enclosing", ["{", '"', None])
@pytest.mark.parametrize("default_enclosing", ["{", '"'])
@pytest.mark.parametrize("enclose_ints", [True, False], ids=["enclose_ints", "no_enclose_ints"])
@pytest.mark.parametrize("reuse_previous_enclosing", [True, False], ids=["reuse", "no_reuse"])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_addition_of_enclosing_on_string(
    metadata_enclosing: str,
    default_enclosing: str,
    enclose_ints: bool,
    reuse_previous_enclosing: bool,
    inplace: bool,
):
    input_string = String(
        start_line=5,
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        value="someValue",  # Value edge-cases are tested in Entry test
    )
    input_string_copy = deepcopy(input_string)

    if metadata_enclosing is not None:
        input_string.parser_metadata["removed_enclosing"] = metadata_enclosing

    middleware = AddEnclosingMiddleware(
        allow_inplace_modification=inplace,
        default_enclosing=default_enclosing,
        reuse_previous_enclosing=reuse_previous_enclosing,
        enclose_integers=enclose_ints,  # This should not impact String
    )

    transformed_library = middleware.transform(library=Library([input_string]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.strings) == 1
    # Assert correct addition of enclosing
    transformed = transformed_library.strings[0]
    changed_value = transformed.value

    # Figure out which enclosing was added
    used_enclosing = _figure_out_added_enclosing(changed_value, input_string.value)

    # Assert correct enclosing was added
    if reuse_previous_enclosing and metadata_enclosing is not None:
        expected_enclosing = metadata_enclosing
    else:
        # Note: `enclose_integers` param is not relevant for String
        expected_enclosing = default_enclosing

    assert used_enclosing == expected_enclosing

    # Assert remaining fields are unchanged
    assert transformed.start_line == input_string_copy.start_line
    assert transformed.raw == input_string_copy.raw
    assert transformed.key == input_string_copy.key

    # Assert `allow_inplace_modification` is respected
    assert_inplace_is_respected(inplace, input_string, transformed)


@pytest.mark.parametrize("block", ["preamble", "implicit_comment", "explicit_comment"])
@pytest.mark.parametrize("reuse_encoding", [True, False], ids=["reuse", "no_reuse"])
@pytest.mark.parametrize("enclose_int", [True, False], ids=["enclose_int", "no_enclose_int"])
@pytest.mark.parametrize("default_enc", ["{", '"'])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_no_addition_block_types(
    block: str, reuse_encoding: bool, enclose_int: bool, default_enc: str, inplace: bool
):
    assert_block_does_not_change(
        block_type=block,
        middleware=AddEnclosingMiddleware(
            reuse_previous_enclosing=reuse_encoding,
            enclose_integers=enclose_int,
            default_enclosing=default_enc,
            allow_inplace_modification=inplace,
        ),
        same_instance=inplace,
    )


# TODO round-trip tests (removal -> addition -> removal)
