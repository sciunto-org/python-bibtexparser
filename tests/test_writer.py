"""Testing the writer, i.e., the deserialized-to-bibtex-converter."""

import pytest

from bibtexparser import BibtexFormat
from bibtexparser import Library
from bibtexparser import writer
from bibtexparser.model import Entry
from bibtexparser.model import ExplicitComment
from bibtexparser.model import Field
from bibtexparser.model import ImplicitComment
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.model import Preamble
from bibtexparser.model import String

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


@pytest.mark.parametrize("value_column", [None, 10, "auto"])
def test_string_value_column(value_column):
    library = Library(
        blocks=[
            String(key="me", value='"myValue"'),
            String(key="veryverylongkey", value='"otherValue"'),
        ]
    )
    bib_format = BibtexFormat()
    if value_column is not None:
        bib_format.value_column = value_column
    string = writer.write(library, bib_format)
    if value_column is None:
        # Make sure there are no unneeded spaces
        assert '@string{me = "myValue"}' in string
        assert '@string{veryverylongkey = "otherValue"}' in string
    elif value_column == 10:
        assert '@string{me      = "myValue"}' in string
        assert '@string{veryverylongkey = "otherValue"}' in string
    if value_column == "auto":
        assert '@string{me              = "myValue"}' in string
        assert '@string{veryverylongkey = "otherValue"}' in string


def test_auto_value_column_considers_string_keys():
    library = Library(blocks=[String(key="averyverylongstringkey", value='"v"'), _dummy_entry()])
    bib_format = BibtexFormat()
    bib_format.value_column = "auto"
    string = writer.write(library, bib_format)
    # The 22-char string key drives the alignment column for entry fields, too
    pad = " " * (22 - len("title"))
    assert f'{bib_format.indent}title{pad} = "myTitle"' in string


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


def test_write_failed_block_preserves_raw_by_default():
    """Writing a parsed failure must not modify its only authoritative representation."""
    raw = "@article{irrelevant-for-this-test,\nexcept = {that-there-need-to-be},\nother = {multiple-lines}\n}"
    block = ParsingFailedBlock(error=ValueError("Some error"), raw=raw, ignore_error_block=None)
    library = Library(blocks=[block])
    string = writer.write(library)

    assert string == raw


def test_write_failed_block_can_retain_legacy_annotation():
    """Annotation remains opt-in for callers that want failures embedded in output."""
    raw = "@article{broken,\ntitle = {Unclosed entry}"
    block = ParsingFailedBlock(error=ValueError("Some error"), raw=raw)
    bibtex_format = BibtexFormat()
    bibtex_format.failed_block_policy = "annotate"

    string = writer.write(Library(blocks=[block]), bibtex_format)

    assert string == "% WARNING Parsing failed for the following 2 lines.\n" + raw + "\n"


def test_write_failed_block_uses_configured_comment():
    """Failed-block output must honor the public format setting and line placeholder."""
    raw = "@article{broken,\ntitle = {Unclosed entry}"
    block = ParsingFailedBlock(error=ValueError("Some error"), raw=raw)
    bibtex_format = BibtexFormat()
    bibtex_format.failed_block_policy = "annotate"
    bibtex_format.parsing_failed_comment = "% CUSTOM FAILURE ({n} source lines)"

    string = writer.write(Library(blocks=[block]), bibtex_format)

    assert string.startswith("% CUSTOM FAILURE (2 source lines)\n")


def test_write_failed_block_can_fail_closed():
    """Strict consumers can require resolution of every retained parse failure."""
    first = ParsingFailedBlock(error=ValueError("first error"), raw="@article(first)")
    second = ParsingFailedBlock(error=ValueError("second error"), raw="@article(second)")
    bibtex_format = BibtexFormat()
    bibtex_format.failed_block_policy = "raise"

    with pytest.raises(ValueError, match="(?s)first error.*second error"):
        writer.write(Library(blocks=[first, second]), bibtex_format)


def test_failed_block_policy_rejects_unknown_value():
    """A misspelled integrity policy must fail instead of selecting accidental behavior."""
    bibtex_format = BibtexFormat()

    with pytest.raises(ValueError, match="preserve.*annotate.*raise"):
        bibtex_format.failed_block_policy = "discard"


def test_write_failed_block_without_raw_raises():
    """A failed block with no raw bibtex cannot be written (issue #400)."""
    block = ParsingFailedBlock(error=ValueError("Some error"), raw=None, ignore_error_block=None)
    library = Library(blocks=[block])
    with pytest.raises(ValueError, match="failed blocks without raw bibtex"):
        writer.write(library)


def test_write_manually_created_duplicate_entries_raises():
    """Reproduces issue #400: duplicate keys on programmatically created entries."""
    library = Library()
    library.add(_dummy_entry())
    # Silently-added duplicates (no raw bibtex) must still be caught at write time.
    library.add(_dummy_entry(), fail_on_duplicate_key=False)
    with pytest.raises(ValueError, match="failed_blocks"):
        writer.write(library)


def test_write_raises_listing_all_unwritable_blocks():
    first = ParsingFailedBlock(error=ValueError("first error"), raw=None)
    second = ParsingFailedBlock(error=ValueError("second error"), raw=None)
    library = Library(blocks=[first, _dummy_entry(), second])
    with pytest.raises(ValueError, match="(?s)first error.*second error"):
        writer.write(library)
