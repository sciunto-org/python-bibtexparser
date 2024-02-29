"""Testing the latex de- and encoding middleware.

Note: All encoding/decoding is done using the pylatexenc library.
Thus, we merely test that the middleware is correctly configured."""

from copy import deepcopy

import pytest

from bibtexparser import Library
from bibtexparser.middlewares.latex_encoding import LatexDecodingMiddleware
from bibtexparser.middlewares.latex_encoding import LatexEncodingMiddleware
from bibtexparser.model import Entry
from bibtexparser.model import Field
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


def _entry_with_latex_string(latex_string):
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
            )
        ],
    )
