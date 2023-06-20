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

    tested_field: Field = library.entries[0].fields_dict[field_key]
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
    assert library.entries[0].fields_dict["firstfield"].value == expected


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
    assert library.entries[0].fields_dict["firstfield"].value == "{some value}"
    assert (
        library.entries[0].fields_dict["fieldBeforeTrailingComma"].value
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

    assert block.ignore_error_block is not None

    title_fields = [f for f in block.ignore_error_block.fields if f.key == "title"]
    assert len(title_fields) == 3
    assert title_fields[0].value == "{The first title}"
    assert title_fields[1].value == "{The second title}"
    assert title_fields[2].value == "{The third title}"

    author_fields = [f for f in block.ignore_error_block.fields if f.key == "author"]
    assert len(author_fields) == 2
    assert author_fields[0].value == "{The first author}"
    assert author_fields[1].value == "{The second author}"

    journal_field = [f for f in block.ignore_error_block.fields if f.key == "journal"]
    assert len(journal_field) == 1
    assert journal_field[0].value == "{Some journal}"


@pytest.mark.parametrize(
    "entry_without_fields",
    [
        # common in revtex, see issue #384
        pytest.param("@article{articleTestKey}", id="without comma"),
        pytest.param("@article{articleTestKey,}", id="with comma"),
    ],
)
def test_entry_without_fields(entry_without_fields: str):
    """For motivation why we need this, please see issue #384"""
    subsequent_article = "@Article{subsequentArticle, title = {Some title}}"
    full_bibtex = f"{entry_without_fields}\n\n{subsequent_article}"
    library: Library = Splitter(full_bibtex).split()
    assert len(library.entries) == 2
    assert len(library.failed_blocks) == 0

    assert library.entries[0].key == "articleTestKey"
    assert len(library.entries[0].fields) == 0

    assert library.entries[1].key == "subsequentArticle"
    assert len(library.entries[1].fields) == 1
