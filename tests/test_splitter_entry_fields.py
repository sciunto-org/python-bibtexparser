import pytest as pytest

from bibtexparser.library import Library
from bibtexparser.model import Field
from bibtexparser.splitter import Splitter


@pytest.mark.parametrize("field_key,value,line", [
    ("year", "2019", 1),
    ("month", "1", 2),
    ("author", '"John Doe"', 3),
])
def test_parse_int_field(field_key: str, value: str, line: int):
    bibtex_str = """@article{test,
    year = 2019,
    month = 1,
    author = "John Doe"
    }"""
    library: Library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert len(library.entries[0].fields) == 3

    tested_field: Field = library.entries[0].fields[field_key]
    assert tested_field.key == field_key
    assert tested_field.value == value
    assert tested_field.start_line == line


