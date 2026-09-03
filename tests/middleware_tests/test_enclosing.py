from copy import deepcopy

import pytest

import bibtexparser
from bibtexparser.library import Library
from bibtexparser.middlewares.enclosing import AddEnclosingMiddleware
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.middleware import BlockMiddleware
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


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("{intro} # {outro}", id="brace_concatenation"),
        pytest.param('"intro" # "outro"', id="quote_concatenation"),
        pytest.param('{intro} # "outro"', id="mixed_concatenation"),
        pytest.param("{a} and {b}", id="two_brace_groups"),
        pytest.param('"a" "b"', id="two_quote_groups"),
        pytest.param("{a} # b # {c}", id="concatenation_with_reference"),
    ],
)
def test_no_removal_if_delimiters_do_not_enclose_whole_value(value: str):
    """Values whose first and last char are delimiters, but not a matching pair,
    must not be stripped, as this would corrupt them."""
    field = Field(value=value, start_line=6, key="pages")
    input_entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[field],
    )

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=True)
    transformed = middleware.transform(library=Library([input_entry])).entries[0]

    assert transformed["pages"] == value
    assert transformed.parser_metadata["removed_enclosing"]["pages"] == "no-enclosing"
    assert transformed.fields_dict["pages"].enclosing == "no-enclosing"


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("{intro} # {outro}", id="brace_concatenation"),
        pytest.param('"intro" # "outro"', id="quote_concatenation"),
        pytest.param("{a} and {b}", id="two_brace_groups"),
    ],
)
def test_no_removal_on_string_block_if_delimiters_do_not_enclose_whole_value(value: str):
    """Same as above, for `@string` blocks."""
    input_string = String(
        start_line=5,
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        value=value,
    )

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=True)
    transformed = middleware.transform(library=Library([input_string])).strings[0]

    assert transformed.value == value
    assert transformed.parser_metadata["removed_enclosing"] == "no-enclosing"
    assert transformed.enclosing == "no-enclosing"


@pytest.mark.parametrize(
    "value, expected_stripped, expected_enclosing",
    [
        pytest.param("{a {b} c}", "a {b} c", "{", id="nested_group"),
        pytest.param("{{nested}}", "{nested}", "{", id="doubly_braced"),
        pytest.param("{}", "", "{", id="empty_braces"),
        pytest.param('""', "", '"', id="empty_quotes"),
        pytest.param('{"quoted"}', '"quoted"', "{", id="quotes_in_braces"),
        pytest.param('"a {b} c"', "a {b} c", '"', id="braces_in_quotes"),
        pytest.param('"a {"} c"', 'a {"} c', '"', id="braced_quote_in_quotes"),
        pytest.param(r"{a \{ b}", r"a \{ b", "{", id="escaped_open_brace"),
        pytest.param(r"{a \} b}", r"a \} b", "{", id="escaped_close_brace"),
        pytest.param(r'"a \" b"', r"a \" b", '"', id="escaped_quote"),
        pytest.param(r"{{\`a} {\`a}}", r"{\`a} {\`a}", "{", id="enclosed_groups"),
    ],
)
def test_removal_of_genuinely_enclosing_delimiters(
    value: str, expected_stripped: str, expected_enclosing: str
):
    """Values that really are enclosed by a single delimiter pair must still be stripped."""
    assert RemoveEnclosingMiddleware._strip_enclosing(value) == (
        expected_stripped,
        expected_enclosing,
    )


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param(" ", id="whitespace"),
        pytest.param("{", id="lone_open_brace"),
        pytest.param("}", id="lone_close_brace"),
        pytest.param('"', id="lone_quote"),
        pytest.param("\\", id="lone_backslash"),
    ],
)
def test_degenerate_values_are_not_stripped(value: str):
    """Short/degenerate values must neither raise nor lose characters."""
    assert RemoveEnclosingMiddleware._strip_enclosing(value) == (value.strip(), "no-enclosing")


def test_concatenation_roundtrip():
    """Default parse -> write must reproduce concatenations of delimited parts
    verbatim, rather than corrupting them."""
    bibtex = '@article{a,\n\tpages = {intro} # {outro},\n\ttitle = "x" # "y"\n}\n'
    written = bibtexparser.write_string(bibtexparser.parse_string(bibtex))

    assert "pages = {intro} # {outro}" in written
    assert 'title = "x" # "y"' in written
    assert written == bibtex


@pytest.mark.parametrize(
    "value, expected_stripped, expected_enclosing",
    [
        pytest.param(r"{\\}a}", r"\\}a", "{", id="doubled_backslash_before_brace"),
        pytest.param(r"{a\\{}", r"a\\{", "{", id="doubled_backslash_before_open_brace"),
        pytest.param(r'"\\""', r'\\"', '"', id="doubled_backslash_before_quote"),
    ],
)
def test_escaping_follows_the_splitter_convention(
    value: str, expected_stripped: str, expected_enclosing: str
):
    """A delimiter is escaped iff directly preceded by a backslash.

    This is the convention of the splitter's mark regex, which skips such a
    delimiter regardless of how many backslashes precede it. The two must agree,
    or values the parser read as a single group are not stripped here.
    """
    assert RemoveEnclosingMiddleware._strip_enclosing(value) == (
        expected_stripped,
        expected_enclosing,
    )


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("Doe, John and Roe, Jane", id="top_level_comma"),
        pytest.param("Foo # , Bar", id="concatenation_with_top_level_comma"),
        pytest.param("a = b", id="top_level_equals"),
        pytest.param("a\nb", id="top_level_newline"),
        pytest.param("a} b", id="unbalanced_closing_brace"),
        pytest.param("{a b", id="unbalanced_opening_brace"),
    ],
)
def test_no_enclosing_demand_is_overruled_for_unwritable_values(value: str):
    """A `no-enclosing` demand must not produce bibtex that does not parse back.

    A value-transforming middleware may change a value after the demand was set
    (e.g. by removing the braces it was derived from), which can leave a value
    that the splitter would not read back in one piece.
    """
    field = Field(value=value, start_line=6, key="author", enclosing="no-enclosing")
    entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[field],
    )

    middleware = AddEnclosingMiddleware(
        reuse_previous_enclosing=True, enclose_integers=True, default_enclosing="{"
    )
    transformed = middleware.transform(library=Library([entry])).entries[0]

    assert transformed["author"] == f"{{{value}}}"


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("jan", id="string_reference"),
        pytest.param("intro # outro", id="concatenation_of_references"),
        pytest.param("{intro} # {outro}", id="concatenation_of_groups"),
        pytest.param("ieeetc # {, Special Issue}", id="mixed_concatenation"),
        pytest.param('"a, b" # c', id="quoted_part_with_comma"),
    ],
)
def test_no_enclosing_demand_is_honored_for_writable_values(value: str):
    """Values that do parse back verbatim keep their `no-enclosing` demand."""
    field = Field(value=value, start_line=6, key="author", enclosing="no-enclosing")
    entry = Entry(
        start_line=5,
        entry_type="article",
        raw="<--- does not matter for this unit test -->",
        key="someKey",
        fields=[field],
    )

    middleware = AddEnclosingMiddleware(
        reuse_previous_enclosing=True, enclose_integers=True, default_enclosing="{"
    )
    transformed = middleware.transform(library=Library([entry])).entries[0]

    assert transformed["author"] == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("{Doe, John} and {Roe, Jane}", id="two_brace_groups"),
        pytest.param("{Foo} # {, Bar}", id="concatenation_of_groups"),
        pytest.param("ieeetc # {, Special Issue}", id="mixed_concatenation"),
    ],
)
def test_written_output_reparses_after_a_value_transformation(value: str):
    """Values kept verbatim carry their own delimiters and a `no-enclosing` demand.

    A middleware rewriting such a value (here: removing the braces) must not
    leave output that bibtexparser can no longer parse.
    """

    class _BraceRemovingMiddleware(BlockMiddleware):
        def transform_entry(self, entry, library):
            for field in entry.fields:
                # As the latex middlewares do: the value setter resets `enclosing`.
                enclosing = field.enclosing
                field.value = field.value.replace("{", "").replace("}", "")
                field.enclosing = enclosing
            return entry

    bibtex = f"@article{{a,\n\tauthor = {value}\n}}\n"
    library = bibtexparser.parse_string(bibtex, append_middleware=[_BraceRemovingMiddleware()])
    written = bibtexparser.write_string(library)

    reparsed = bibtexparser.parse_string(written)
    assert not reparsed.failed_blocks
    assert len(reparsed.entries) == 1
