from copy import deepcopy

import pytest

import bibtexparser
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
    value: str | int,
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


@pytest.mark.parametrize("demanded_enclosing", ["{", '"', "no-enclosing"])
@pytest.mark.parametrize("metadata_enclosing", ["{", '"', "no-enclosing", None])
@pytest.mark.parametrize("default_enclosing", ["{", '"'])
@pytest.mark.parametrize("reuse_previous_enclosing", [True, False], ids=["reuse", "no_reuse"])
def test_demanded_enclosing_takes_precedence_on_entry(
    demanded_enclosing: str,
    metadata_enclosing: str,
    default_enclosing: str,
    reuse_previous_enclosing: bool,
):
    """A `field.enclosing` demand must win over all other enclosing rules. See issue #447."""
    field = Field(key="month", value="jan", start_line=6, enclosing=demanded_enclosing)
    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[field],
    )
    if metadata_enclosing is not None:
        input_entry.parser_metadata["removed_enclosing"] = {"month": metadata_enclosing}

    middleware = AddEnclosingMiddleware(
        allow_inplace_modification=True,
        default_enclosing=default_enclosing,
        reuse_previous_enclosing=reuse_previous_enclosing,
        enclose_integers=True,
    )

    transformed = middleware.transform(library=Library([input_entry])).entries[0]

    expected = {"{": "{jan}", '"': '"jan"', "no-enclosing": "jan"}[demanded_enclosing]
    assert transformed["month"] == expected
    # The demand is consumed when the new (enclosed) value is assigned
    assert transformed.fields_dict["month"].enclosing is None


@pytest.mark.parametrize("value", [8, "8"], ids=["int", "digit-str"])
def test_demanded_no_enclosing_on_int_value(value):
    """Demanding 'no-enclosing' on an int field must yield an unenclosed string value."""
    field = Field(key="month", value=value, start_line=6, enclosing="no-enclosing")
    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[field],
    )

    middleware = AddEnclosingMiddleware(
        allow_inplace_modification=True,
        default_enclosing="{",
        reuse_previous_enclosing=False,
        enclose_integers=True,
    )

    transformed = middleware.transform(library=Library([input_entry])).entries[0]
    assert transformed["month"] == "8"


@pytest.mark.parametrize("demanded_enclosing", ["{", '"', "no-enclosing"])
def test_demanded_enclosing_takes_precedence_on_string(demanded_enclosing: str):
    input_string = String(
        start_line=5,
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        value="intro # outro",
        enclosing=demanded_enclosing,
    )

    middleware = AddEnclosingMiddleware(
        allow_inplace_modification=True,
        default_enclosing="{",
        reuse_previous_enclosing=False,
        enclose_integers=True,
    )

    transformed = middleware.transform(library=Library([input_string])).strings[0]
    expected = {
        "{": "{intro # outro}",
        '"': '"intro # outro"',
        "no-enclosing": "intro # outro",
    }[demanded_enclosing]
    assert transformed.value == expected
    assert transformed.enclosing is None


def test_removal_sets_no_enclosing_demand_for_references():
    """Unenclosed non-numeric values (i.e., string references and concatenations)
    must keep their `no-enclosing` when writing. See issue #447."""
    fields = [
        Field(value="jan", start_line=6, key="month"),
        Field(value='jan # "~1st"', start_line=7, key="day"),
        Field(value="2019", start_line=8, key="year"),
        Field(value="{Some Title}", start_line=9, key="title"),
        Field(value='"Some Author"', start_line=10, key="author"),
    ]
    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=fields,
    )

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=True)
    transformed = middleware.transform(library=Library([input_entry])).entries[0]

    # References and concatenations demand to remain unenclosed
    assert transformed.fields_dict["month"].enclosing == "no-enclosing"
    assert transformed.fields_dict["day"].enclosing == "no-enclosing"
    # Ints remain subject to the writer's `enclose_integers` option
    assert transformed.fields_dict["year"].enclosing is None
    # Previously enclosed values remain subject to the writer's defaults
    assert transformed.fields_dict["title"].enclosing is None
    assert transformed.fields_dict["author"].enclosing is None


def test_removal_sets_no_enclosing_demand_on_string_block():
    input_string = String(
        start_line=5,
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        value="intro # outro",
    )

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=True)
    transformed = middleware.transform(library=Library([input_string])).strings[0]
    assert transformed.enclosing == "no-enclosing"


def test_string_reference_roundtrip():
    """Default parse -> write must not enclose string references and concatenations,
    as this would change their semantics. See issue #447."""
    bibtex = '@article{someKey,\n\tmonth = jan,\n\tpages = intro # "--" # outro,\n\tyear = 2019\n}'
    library = bibtexparser.parse_string(bibtex)
    written = bibtexparser.write_string(library)

    assert "month = jan" in written
    assert 'pages = intro # "--" # outro' in written
    # Ints are still enclosed by the default unparse stack
    assert "year = {2019}" in written


# TODO round-trip tests (removal -> addition -> removal)
