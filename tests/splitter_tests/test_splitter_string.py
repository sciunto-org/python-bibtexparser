import pytest

from bibtexparser.library import Library
from bibtexparser.splitter import Splitter
from tests.resources import EDGE_CASE_VALUES
from tests.resources import ENCLOSINGS


@pytest.mark.parametrize(
    "key",
    [
        "ICSE2022",
        "ICSE2022-with-dash",
        "ICSE2022_with_underscore",
        "ICSE2022_with_underscore_and-dash",
    ],
)
@pytest.mark.parametrize("value", EDGE_CASE_VALUES + [""])
@pytest.mark.parametrize("enclosing", ENCLOSINGS)
def test_parse_string_key_val(key: str, value: str, enclosing: str):
    """Test that the string is correctly parsed."""
    enclosed_value = enclosing.format(value)
    bibtex_str = f"""@string{{{key} = {enclosed_value}}}"""
    library: Library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.strings) == 1
    assert library.strings[0].key == key
    assert library.strings[0].value == enclosed_value
    assert library.strings[0].start_line == 0


@pytest.mark.parametrize("enclosing", ENCLOSINGS)
def test_parse_empty_string(enclosing: str):
    """Test that the string is correctly parsed."""
    empty_enclosing = enclosing.format("")
    bibtex_str = f"""@string{{key = {empty_enclosing}}}"""
    library: Library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.strings) == 1
    assert library.strings[0].key == "key"
    assert library.strings[0].value == empty_enclosing
