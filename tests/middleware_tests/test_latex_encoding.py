"""Testing the latex de- and encoding middleware.

Note: All encoding/decoding is done using the pylatexenc library.
Thus, we merely test that the middleware is correctly configured."""
from copy import deepcopy
from textwrap import dedent

import pytest

from bibtexparser import Library
from bibtexparser.middlewares.latex_encoding import LatexDecodingMiddleware, LatexEncodingMiddleware
from bibtexparser.model import Entry, Field
from tests.middleware_tests.middleware_test_util import assert_nonfield_entry_attributes_unchanged


@pytest.mark.parametrize("latex_string,expected_decoded_string", [
    pytest.param(r"some \textbf{bold} text", "some bold text", id=r"\textbf"),
    pytest.param(r"Kristoffer H\o{}gsbro Rose", "Kristoffer Høgsbro Rose", id=r"\o{}"),
    pytest.param(r"Einstein $ e=m_c^2 $", "Einstein $ e=m_c^2 $", id=r"Keep math mode"),
    pytest.param(r"I payed \$10", "I payed $10", id=r"Keep \$"),
    pytest.param(r"{Walther Andreas} Muller", "{Walther Andreas} Muller", id=r"Keep braces"),
    pytest.param(r"See \url{mweiss.ch}", r"See mweiss.ch", id=r"Remove \url{...}"),
    pytest.param(r"See \url{https://human_resources.com", r"See https://human_resources.com",
                 id="Keep special chars in url")
])
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
    transformed_field = transformed_entry.fields["tested_field"]

    assert transformed_field.value == expected_decoded_string

    # Make sure other attributes are not changed
    assert_nonfield_entry_attributes_unchanged(original_copy, transformed_entry)


@pytest.mark.parametrize("human_string ,expected_latex_string", [
    pytest.param("Kristoffer Høgsbro Rose", r"Kristoffer H{\o}gsbro Rose", id=r"\o{}"),
    pytest.param(r"Einstein $ e=m_c^2 $", r"Einstein $ e=m_c^2 $", id=r"Keep math mode"),
    pytest.param(r"I payed $10", r"I payed \$10", id=r"Escape $"),
    # TODO the following case rightfully fails. I have to think about that.
    #   Maybe I'll have to change the decoding defaults (to remove brackets) for consistency.
    pytest.param(r"{Walther Andreas} Muller", r"{Walther Andreas} Muller", id=r"Keep braces"),
])
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
    transformed_field = transformed_entry.fields["tested_field"]

    assert transformed_field.value == expected_latex_string

    # Make sure other attributes are not changed
    assert_nonfield_entry_attributes_unchanged(original_copy, transformed_entry)


def _entry_with_latex_string(latex_string):
    return Entry(
        start_line=1,
        raw="Not relevant for this test",
        entry_type="article",
        key="someEntry",
        fields={
            "tested_field": Field(
                start_line=1,
                key="tested_field",
                value=latex_string,
            )
        }
    )
