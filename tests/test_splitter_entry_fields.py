import pytest as pytest

from bibtexparser.library import Library
from bibtexparser.model import Field
from bibtexparser.splitter import Splitter


@pytest.mark.parametrize("field_key,value,line", [
    ("year", "2019", 1),
    ("month", "1", 2),
    ("author", '"John Doe"', 3),
    ("journal", "someJournalReference", 4),
])
def test_field_enclosings(field_key: str, value: str, line: int):
    """Test that the enclosings of the fields are correctly parsed.

    Valid enclosings are:
    - double quotes
    - curly braces
    - no enclosings (for integers or String references)
    """
    bibtex_str = """@article{test,
    year = 2019,
    month = 1,
    author = "John Doe",
    journal = someJournalReference
    }"""
    library: Library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert len(library.entries[0].fields) == 4

    tested_field: Field = library.entries[0].fields[field_key]
    assert tested_field.key == field_key
    assert tested_field.value == value
    assert tested_field.start_line == line


@pytest.mark.parametrize("declared_block_type,expected", [
    ("@article", "article"),
    ("@ARTICLE", "article"),
    ("@Article", "article"),
    ("@book", "book"),
    ("@BOOK", "book"),
    ("@Book", "book"),
    ("@inbook", "inbook"),
    ("@INBOOK", "inbook"),
    ("@Inbook", "inbook"),
    ("@incollection", "incollection"),
    ("@INCOLLECTION", "incollection"),
    ("@Incollection", "incollection"),
    ("@inproceedings", "inproceedings"),
    ("@INPROCEEDINGS", "inproceedings"),
    ("@InprocEEdings", "inproceedings"),
])
def test_entry_type(declared_block_type, expected):
    """Test that the entry type is case insensitive."""
    bibtex_str = """@article{test,
    author = "John Doe"
    }"""
    bibtex_str = bibtex_str.replace("@article", declared_block_type)
    library: Library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert library.entries[0].entry_type == expected
