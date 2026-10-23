"""Testing the latex de- and encoding middleware.

Note: All encoding/decoding is done using the pylatexenc library.
Thus, we merely test that the middleware is correctly configured."""

from copy import deepcopy

import pytest
from pylatexenc.latex2text import LatexNodes2Text

import bibtexparser
from bibtexparser import Library
from bibtexparser.exceptions import PartialMiddlewareException
from bibtexparser.middlewares.latex_encoding import LatexDecodingMiddleware
from bibtexparser.middlewares.latex_encoding import LatexEncodingMiddleware
from bibtexparser.middlewares.latex_encoding import _PyStringTransformerMiddleware
from bibtexparser.model import Entry
from bibtexparser.model import Field
from bibtexparser.model import MiddlewareErrorBlock
from bibtexparser.model import String
from tests.middleware_tests.middleware_test_util import assert_inplace_is_respected
from tests.middleware_tests.middleware_test_util import assert_nonfield_entry_attributes_unchanged


@pytest.mark.parametrize(
    "latex_string,expected_decoded_string",
    [
        pytest.param(r"some \textbf{bold} text", "some bold text", id=r"\textbf"),
        pytest.param(r"Kristoffer H\o{}gsbro Rose", "Kristoffer Høgsbro Rose", id=r"\o{}"),
        pytest.param(r"Einstein $ e=m_c^2 $", "Einstein $ e=m_c^2 $", id=r"Keep math mode"),
        pytest.param(r"I payed \$10", "I payed $10", id=r"Keep \$"),
        pytest.param(
            r"{Walther Andreas} Muller",
            "Walther Andreas Muller",
            id=r"Remove braces-wrapping",
        ),
        pytest.param(r"See \url{mweiss.ch}", r"See mweiss.ch", id=r"Remove \url{...}"),
        pytest.param(
            r"See \url{https://human_resources.com",
            r"See https://human_resources.com",
            id="Keep special chars in url",
        ),
        pytest.param(
            r"One Two and Three{\'\i}abc-Four{\'\i}def",
            "One Two and Threeíabc-Fourídef",
            id=r"Remove braces-wrapping",
        ),
    ],
)
def test_latex_special_chars_decoding(latex_string, expected_decoded_string):
    """Test that latex special chars are decoded correctly,

    with default settings (math mode disabled, keep braces)"""
    input_entry = _entry_with_latex_string(latex_string)
    library = Library([input_entry])
    original_copy = deepcopy(input_entry)

    middleware = LatexDecodingMiddleware(allow_inplace_modification=True)
    transformed_library = middleware.transform(library)

    assert len(transformed_library.entries) == 1
    assert len(transformed_library.blocks) == 1

    transformed_entry = transformed_library.entries[0]
    transformed_field = transformed_entry.fields_dict["tested_field"]

    assert transformed_field.value == expected_decoded_string

    # Make sure other attributes are not changed
    assert_nonfield_entry_attributes_unchanged(original_copy, transformed_entry)


@pytest.mark.parametrize(
    "human_string ,expected_latex_string",
    [
        pytest.param("Kristoffer Høgsbro Rose", r"Kristoffer H{\o}gsbro Rose", id=r"\o{}"),
        pytest.param(r"Einstein $ e=m_c^2 $", r"Einstein $ e=m_c^2 $", id=r"Keep math mode"),
        pytest.param(r"I payed $10", r"I payed \$10", id=r"Escape $"),
        pytest.param(
            r"See https://mweiss.ch",
            r"See \url{https://mweiss.ch}",
            id=r"\url{...} for https",
        ),
        pytest.param(
            r"See http://mweiss.ch",
            r"See \url{http://mweiss.ch}",
            id=r"\url{...} for http",
        ),
        pytest.param(r"See www.mweiss.ch", r"See \url{www.mweiss.ch}", id=r"\url{...} for www."),
        pytest.param(
            r"See https://www.mweiss.ch",
            r"See \url{https://www.mweiss.ch}",
            id=r"\url{...} for https://www.",
        ),
    ],
)
def test_latex_special_chars_encoding(human_string, expected_latex_string):
    """Test that latex special chars are encoded correctly,

    with default settings (math mode disabled, keep braces)"""
    input_entry = _entry_with_latex_string(human_string)
    library = Library([input_entry])
    original_copy = deepcopy(input_entry)

    middleware = LatexEncodingMiddleware(allow_inplace_modification=True)
    transformed_library = middleware.transform(library)

    assert len(transformed_library.entries) == 1
    assert len(transformed_library.blocks) == 1

    transformed_entry = transformed_library.entries[0]
    transformed_field = transformed_entry.fields_dict["tested_field"]

    assert transformed_field.value == expected_latex_string

    # Make sure other attributes are not changed
    assert_nonfield_entry_attributes_unchanged(original_copy, transformed_entry)


@pytest.mark.parametrize(
    "middleware_class,input_value,expected_value",
    [
        pytest.param(LatexDecodingMiddleware, r"M{\"u}ller", "Müller", id="decoding"),
        pytest.param(LatexEncodingMiddleware, "Müller", r"M\"uller", id="encoding"),
    ],
)
def test_string_block_value_transformation(middleware_class, input_value, expected_value):
    """String block values must be transformed like field values (issue #529)."""
    library = Library([String(key="me", value=input_value, start_line=1, raw="irrelevant")])

    transformed_library = middleware_class(allow_inplace_modification=True).transform(library)

    transformed_value = transformed_library.strings[0].value
    assert isinstance(transformed_value, str)
    assert transformed_value == expected_value


def test_failing_string_transformation_becomes_error_block():
    """Transformation errors on String blocks must not be swallowed (issue #529)."""

    class _FailingMiddleware(_PyStringTransformerMiddleware):
        """Test dummy that fails on every value."""

        # docstr-coverage: inherited
        @classmethod
        def metadata_key(cls) -> str:
            return "failing_test_middleware"

        # docstr-coverage: inherited
        def _transform_python_value_string(self, python_string: str) -> tuple[str, str]:
            return python_string, "some error"

    library = Library([String(key="me", value="some value", start_line=1, raw="irrelevant")])

    transformed_library = _FailingMiddleware(allow_inplace_modification=True).transform(library)

    assert len(transformed_library.failed_blocks) == 1
    error_block = transformed_library.failed_blocks[0]
    assert isinstance(error_block, MiddlewareErrorBlock)
    assert isinstance(error_block.error, PartialMiddlewareException)


@pytest.mark.parametrize("inplace", [True, False])
@pytest.mark.parametrize("middleware_class", [LatexEncodingMiddleware, LatexDecodingMiddleware])
def test_inplace(inplace: bool, middleware_class):
    """Make sure that inplace conversion is done iff inplace is True"""
    input_entry = _entry_with_latex_string("Some string")
    library = Library([input_entry])

    middleware = middleware_class(allow_inplace_modification=inplace)
    transformed_library = middleware.transform(library)

    assert len(transformed_library.entries) == 1
    assert len(transformed_library.blocks) == 1

    # Assert `allow_inplace_modification` is respected
    assert_inplace_is_respected(inplace, input_entry, transformed_library.entries[0])


@pytest.mark.parametrize("middleware_class", [LatexEncodingMiddleware, LatexDecodingMiddleware])
@pytest.mark.parametrize("enclosing", ["no-enclosing", "{", '"'])
def test_enclosing_demand_survives_field_transformation(middleware_class, enclosing):
    """Latex de-/encoding changes the representation of a value, not its kind.

    Thus, the enclosing demand (which the `Field.value` setter resets) must be restored."""
    input_entry = _entry_with_latex_string("jan", enclosing=enclosing)

    transformed_library = middleware_class(allow_inplace_modification=True).transform(
        Library([input_entry])
    )

    transformed_field = transformed_library.entries[0].fields_dict["tested_field"]
    assert transformed_field.value == "jan"
    assert transformed_field.enclosing == enclosing


@pytest.mark.parametrize("middleware_class", [LatexEncodingMiddleware, LatexDecodingMiddleware])
@pytest.mark.parametrize("enclosing", ["no-enclosing", "{", '"'])
def test_enclosing_demand_survives_string_transformation(middleware_class, enclosing):
    """Same as `test_enclosing_demand_survives_field_transformation`, for String blocks."""
    input_string = String(
        key="me", value="jan", start_line=1, raw="irrelevant", enclosing=enclosing
    )

    transformed_library = middleware_class(allow_inplace_modification=True).transform(
        Library([input_string])
    )

    transformed_string = transformed_library.strings[0]
    assert transformed_string.value == "jan"
    assert transformed_string.enclosing == enclosing


@pytest.mark.parametrize("middleware_class", [LatexEncodingMiddleware, LatexDecodingMiddleware])
@pytest.mark.parametrize(
    "bibtex",
    [
        pytest.param("@article{someEntry,\n\tmonth = jan\n}", id="entry_string_reference"),
        pytest.param("@string{intro = tro}", id="string_block_reference"),
    ],
)
def test_unenclosed_values_are_written_verbatim(middleware_class, bibtex):
    """Unenclosed values must not be enclosed on write, even with a de-/encoder in the stack."""
    library = bibtexparser.parse_string(
        bibtex, append_middleware=[middleware_class(allow_inplace_modification=True)]
    )
    assert bibtexparser.write_string(library).strip() == bibtex.strip()


def test_concatenation_roundtrips_with_latex_decoding():
    """Concatenation expressions must survive a parse-transform-write roundtrip.

    Note: Only decoding is tested here, as the encoder (correctly, for regular values)
    escapes the `#` of the concatenation itself."""
    bibtex = "@article{someEntry,\n\tpages = intro # outro\n}"
    library = bibtexparser.parse_string(
        bibtex, append_middleware=[LatexDecodingMiddleware(allow_inplace_modification=True)]
    )
    assert bibtexparser.write_string(library).strip() == bibtex.strip()


def test_excluded_fields_preserve_identifiers_after_default_stack_resolution():
    """Excluded fields keep URL-like identifiers while regular text is decoded."""
    bibtex = r"""
    @article{someEntry,
        Title = {An {\"u}ber title},
        URL = url_reference,
        doi = {10.1234/article~id},
        Custom_Url = {https://example.com/custom~id},
        url_extra = {A~regular text value}
    }
    @string{url_reference = {https://example.com/reference~id}}
    """

    library = bibtexparser.parse_string(
        bibtex,
        append_middleware=[LatexDecodingMiddleware(exclude_fields=("uRl", "DOI", "custom_url"))],
    )

    fields = library.entries[0].fields_dict
    assert fields["Title"].value == "An über title"
    assert fields["URL"].value == "https://example.com/reference~id"
    assert fields["doi"].value == "10.1234/article~id"
    assert fields["Custom_Url"].value == "https://example.com/custom~id"
    assert fields["url_extra"].value == "A\xa0regular text value"
    # @string blocks remain subject to transformation. The default parse stack
    # resolves the reference before this middleware sees the entry field.
    assert library.strings[0].value == "https://example.com/reference\xa0id"


@pytest.mark.parametrize(
    "middleware_class,input_value,expected_value",
    [
        pytest.param(LatexDecodingMiddleware, r"M{\"u}ller", "Müller", id="decoding"),
        pytest.param(LatexEncodingMiddleware, "Müller", r"M\"uller", id="encoding"),
    ],
)
def test_excluded_fields_are_case_insensitive_and_exact(
    middleware_class, input_value, expected_value
):
    """An exclusion matches a complete field key, regardless of its casing."""
    entry = Entry(
        start_line=1,
        raw="irrelevant",
        entry_type="article",
        key="someEntry",
        fields=[
            Field(key="URL", value="A~B"),
            Field(key="url_extra", value=input_value),
        ],
    )

    transformed_library = middleware_class(exclude_fields=("url",)).transform(Library([entry]))
    fields = transformed_library.entries[0].fields_dict

    assert fields["URL"].value == "A~B"
    assert fields["url_extra"].value == expected_value


@pytest.mark.parametrize(
    "middleware_class,excluded_value,included_value,expected_included_value",
    [
        pytest.param(
            LatexDecodingMiddleware,
            "A~B",
            r"M{\"u}ller",
            "Müller",
            id="decoding",
        ),
        pytest.param(
            LatexEncodingMiddleware,
            "A~B",
            "Müller",
            r"M\"uller",
            id="encoding",
        ),
    ],
)
def test_excluded_fields_respect_copy_mode_and_enclosing_metadata(
    middleware_class, excluded_value, included_value, expected_included_value
):
    """Skipping a field does not drop its enclosing demand or mutate the input copy."""
    entry = Entry(
        start_line=1,
        raw="irrelevant",
        entry_type="article",
        key="someEntry",
        fields=[
            Field(key="URL", value=excluded_value, enclosing='"'),
            Field(key="title", value=included_value, enclosing="{"),
        ],
    )
    original_copy = deepcopy(entry)

    transformed_library = middleware_class(
        allow_inplace_modification=False, exclude_fields=("url",)
    ).transform(Library([entry]))
    transformed_entry = transformed_library.entries[0]

    assert transformed_entry is not entry
    assert transformed_entry.fields_dict["URL"].value == excluded_value
    assert transformed_entry.fields_dict["URL"].enclosing == '"'
    assert transformed_entry.fields_dict["title"].value == expected_included_value
    assert entry == original_copy


def test_excluded_fields_work_with_custom_decoder():
    """Exclusions apply without replacing a user-provided decoder."""
    entry = Entry(
        start_line=1,
        raw="irrelevant",
        entry_type="article",
        key="someEntry",
        fields=[
            Field(key="url", value="A~B"),
            Field(key="title", value=r"{Walther Andreas} Muller"),
        ],
    )

    decoder = LatexNodes2Text(keep_braced_groups=True)
    transformed_library = LatexDecodingMiddleware(
        decoder=decoder, exclude_fields=("URL",)
    ).transform(Library([entry]))
    fields = transformed_library.entries[0].fields_dict

    assert fields["url"].value == "A~B"
    assert fields["title"].value == "{Walther Andreas} Muller"


def _entry_with_latex_string(latex_string, enclosing=None):
    return Entry(
        start_line=1,
        raw="Not relevant for this test",
        entry_type="article",
        key="someEntry",
        fields=[
            Field(
                start_line=1,
                key="tested_field",
                value=latex_string,
                enclosing=enclosing,
            )
        ],
    )
