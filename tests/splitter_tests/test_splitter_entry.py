"""Tests the parsing of entries, e.g. `@article{...}` blocks."""
from textwrap import dedent

import pytest as pytest

from bibtexparser.library import Library
from bibtexparser.model import DuplicateFieldKeyBlock, Field
from bibtexparser.splitter import Splitter
from tests.resources import EDGE_CASE_VALUES, ENCLOSINGS


@pytest.mark.parametrize(
    "field_key,value,line",
    [
        ("year", "2019", 1),
        ("month", "1", 2),
        ("author", '"John Doe"', 3),
        ("journal", "someJournalReference", 4),
    ],
)
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


@pytest.mark.parametrize(
    "declared_block_type,expected",
    [
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
    ],
)
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


@pytest.mark.parametrize("field_value", EDGE_CASE_VALUES)
@pytest.mark.parametrize("enclosing", ENCLOSINGS)
def test_field_value(field_value: str, enclosing: str):
    """Test that the field values are correctly parsed.

    The primarily tested edge-cases here are special chars,
    such as curly braces, backslashes, etc. in the field values.

    We test all of them for both enclosings (double quotes and curly braces).
    """
    expected = enclosing.format(field_value)
    bibtex_str = f"""@article{{test,
    firstfield = {expected},.
    otherfield = "otherValue"
    }}"""
    library: Library = Splitter(bibtex_str).split()
    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert len(library.entries[0].fields) == 2
    assert library.entries[0].fields["firstfield"].value == expected


@pytest.mark.parametrize(
    "enclosing",
    ENCLOSINGS
    + [
        pytest.param("{0}", id="no enclosing"),
    ],
)
def test_trailing_comma(enclosing: str):
    """Test that a trailing comma is correctly parsed (i.e., ignored)."""
    value_before_trailing_comma = enclosing.format("valueBeforeTrailingComma")
    bibtex_str = dedent(
        f"""\
    @article{{test,
        firstfield = {{some value}},
        fieldBeforeTrailingComma = {value_before_trailing_comma},
    }}
    
    @string{{someString = "some value"}}"""
    )
    library: Library = Splitter(bibtex_str).split()
    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert len(library.entries[0].fields) == 2
    assert library.entries[0].fields["firstfield"].value == "{some value}"
    assert (
        library.entries[0].fields["fieldBeforeTrailingComma"].value
        == value_before_trailing_comma
    )

    # Make sure that subsequent blocks are still parsed correctly
    assert len(library.strings) == 1
    assert library.strings[0].value == '"some value"'
    assert library.strings[0].key == "someString"
    assert library.strings[0].start_line == 5


def test_multiple_identical_field_keys():
    bibtex_str = dedent(
        """\
        @article{test,
            title = {The first title},
            author = {The first author},
            title = {The second title},
            title = {The third title},
            author = {The second author},
            journal = {Some journal}
        }"""
    )
    library: Library = Splitter(bibtex_str).split()

    assert len(library.blocks) == 1
    assert len(library.failed_blocks) == 1

    block = library.failed_blocks[0]
    assert isinstance(block, DuplicateFieldKeyBlock)

    assert "author, title" in str(block.error)

    assert block.entry.fields["title"].value == "{The first title}"
    assert block.entry.fields["title_duplicate_1"].value == "{The second title}"
    assert block.entry.fields["title_duplicate_2"].value == "{The third title}"
    assert block.entry.fields["author"].value == "{The first author}"
    assert block.entry.fields["author_duplicate_1"].value == "{The second author}"
    assert block.entry.fields["journal"].value == "{Some journal}"
    assert len(block.entry.fields) == 6
    assert block.entry.entry_type == "article"
    assert block.entry.key == "test"
