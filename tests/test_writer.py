"""Testing the writer, i.e., the deserialized-to-bibtex-converter."""

import pytest

from bibtexparser import BibtexFormat, Library, writer
from bibtexparser.model import (
    Entry,
    ExplicitComment,
    Field,
    ImplicitComment,
    ParsingFailedBlock,
    Preamble,
    String,
)

_DUMMY_STRING = String(key="myKey", value='"myValue"')
_DUMMY_PREAMBLE = Preamble(value='"myValue"')
_DUMMY_EXPLICIT_COMMENT = ExplicitComment(comment="myValue")
_DUMMY_IMPLICIT_COMMENT = ImplicitComment(comment="#myValue")


def _dummy_entry():
    return Entry(
        entry_type="article",
        key="myKey",
        fields=[
            Field(key="title", value='"myTitle"'),
            Field(key="author", value='"myAuthor"'),
        ],
    )


@pytest.mark.parametrize(
    "block, expected_string",
    [
        (_DUMMY_STRING, '@string{myKey = "myValue"}\n'),
        (_DUMMY_PREAMBLE, '@preamble{"myValue"}\n'),
        (_DUMMY_EXPLICIT_COMMENT, "@comment{myValue}\n"),
        (_DUMMY_IMPLICIT_COMMENT, "#myValue\n"),
    ],
)
def test_single_simple_blocks(block, expected_string):
    """Test the @string serializer."""
    library = Library(blocks=[block])
    string = writer.write(library)
    assert string == expected_string


@pytest.mark.parametrize("indent", [None, "", " ", "\t"])
def test_write_entry_with_indent(indent):
    entry_block = _dummy_entry()
    library = Library(blocks=[entry_block])
    bib_format = BibtexFormat()
    expected_indent = "\t"  # default
    if indent is not None:
        bib_format.indent = indent
        expected_indent = indent

    string = writer.write(library, bib_format)
    assert (
        string == f'@article{{myKey,\n{expected_indent}title = "myTitle",'
        f'\n{expected_indent}author = "myAuthor"\n}}\n'
    )


@pytest.mark.parametrize("trailing_comma", [None, True, False])
def test_write_entry_with_trailing_comma(trailing_comma):
    entry_block = _dummy_entry()
    library = Library(blocks=[entry_block])
    bib_format = BibtexFormat()
    expected = ""  # default
    if trailing_comma is not None:
        bib_format.trailing_comma = trailing_comma
        if trailing_comma:
            expected = ","

    string = writer.write(library, bib_format)
    assert (
        string == f'@article{{myKey,\n\ttitle = "myTitle",'
        f'\n\tauthor = "myAuthor"{expected}\n}}\n'
    )


@pytest.mark.parametrize("value_column", [None, 10, "auto"])
def test_entry_value_column(value_column):
    entry_block = _dummy_entry()
    entry_block.set_field(Field(key="veryverylongkeyfield", value="2020"))
    library = Library(blocks=[entry_block])
    bib_format = BibtexFormat()
    if value_column is not None:
        bib_format.value_column = value_column
    string = writer.write(library, bib_format)
    if value_column is None:
        # Make sure there are no unneeded spaces
        assert f'{bib_format.indent}title = "myTitle"' in string
        assert f'{bib_format.indent}author = "myAuthor"' in string
        assert f"{bib_format.indent}veryverylongkeyfield = 2020" in string
    elif value_column == 10:
        assert f'{bib_format.indent}title   = "myTitle"' in string
        assert f'{bib_format.indent}author  = "myAuthor"' in string
        assert f"{bib_format.indent}veryverylongkeyfield = 2020" in string
    if value_column == "auto":
        assert f'{bib_format.indent}title                = "myTitle"' in string
        assert f'{bib_format.indent}author               = "myAuthor"' in string
        assert f"{bib_format.indent}veryverylongkeyfield = 2020" in string


@pytest.mark.parametrize("block_separator", [None, "\n\n", "\n-----\n"])
def test_block_separator(block_separator):
    library = Library(blocks=[_DUMMY_STRING, _DUMMY_PREAMBLE])
    bib_format = BibtexFormat()
    if block_separator is not None:
        bib_format.block_separator = block_separator
    else:
        block_separator = "\n\n"  # default
    string = writer.write(library, bib_format)
    lines = string.splitlines()

    if block_separator == "\n":
        # Case where the next line immediately is the next block
        assert len(lines) == 2
        assert lines[0] == '@string{myKey = "myValue"}'
        assert lines[1] == '@preamble{"myValue"}'
    else:
        # Case where blocks are separated by at least one line
        expected_lines = block_separator.splitlines()
        for i, l in enumerate(expected_lines):
            assert lines[1 + i] == l

        assert lines[1 + len(expected_lines)] == '@preamble{"myValue"}'


def test_write_failed_block():
    raw = "@article{irrelevant-for-this-test,\nexcept = {that-there-need-to-be},\nother = {multiple-lines}\n}"
    block = ParsingFailedBlock(
        error=ValueError("Some error"), raw=raw, ignore_error_block=None
    )
    library = Library(blocks=[block])
    string = writer.write(library)
    lines = string.splitlines()

    assert len(lines) == 5
    assert lines[0].startswith("% WARNING")
    assert lines[1] == "@article{irrelevant-for-this-test,"
    assert lines[2] == "except = {that-there-need-to-be},"
    assert lines[3] == "other = {multiple-lines}"
    assert lines[4] == "}"
