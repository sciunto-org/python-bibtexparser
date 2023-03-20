"""Testing the writer, i.e., the deserialized-to-bibtex-converter."""

import pytest

from bibtexparser import Library, writer, BibtexFormat
from bibtexparser.model import String, Preamble, ExplicitComment, ImplicitComment, Entry, Field


def test_write_string():
    """Test the @string serializer."""
    string_block = String(key="myKey", value='"myValue"')
    library = Library(blocks=[string_block])
    string = writer.write_string(library)
    assert string == f'@string{{myKey = "myValue"}}'


def test_write_preamble():
    """Test the @preamble serializer."""
    preamble_block = Preamble(value='"myValue"')
    library = Library(blocks=[preamble_block])
    string = writer.write_string(library)
    assert string == f'@preamble{{"myValue"}}'


def test_write_explicit_comment():
    """Test the @comment serializer."""
    comment_block = ExplicitComment(comment="myValue")
    library = Library(blocks=[comment_block])
    string = writer.write_string(library)
    assert string == f'@comment{{myValue}}'


def test_write_implicit_comment():
    """Test the implicit comment serializer."""
    comment_block = ImplicitComment(comment="#myValue")
    library = Library(blocks=[comment_block])
    string = writer.write_string(library)
    assert string == f'#myValue'


@pytest.mark.parametrize("indent", [None, "", " ", "\t"])
def test_write_entry_with_indent(indent):
    entry_block = _dummy_entry()
    library = Library(blocks=[entry_block])
    bib_format = BibtexFormat()
    expected_indent = "\t"  # default
    if indent is not None:
        bib_format.indent = indent
        expected_indent = indent

    string = writer.write_string(library, bib_format)
    assert string == f'@article{{myKey,\n{expected_indent}title = "myTitle",' \
                     f'\n{expected_indent}author = "myAuthor"\n}}'


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

    string = writer.write_string(library, bib_format)
    assert string == f'@article{{myKey,\n\ttitle = "myTitle",' \
                     f'\n\tauthor = "myAuthor"{expected}\n}}'


@pytest.mark.parametrize("value_column", [None, 10, "auto"])
def test_entry_value_column(value_column):
    entry_block = _dummy_entry()
    entry_block.set_field(Field(key="veryverylongkeyfield", value="2020"))
    library = Library(blocks=[entry_block])
    bib_format = BibtexFormat()
    if value_column is not None:
        bib_format.value_column = value_column
    string = writer.write_string(library, bib_format)
    if value_column is None:
        # Make sure there are no unneeded spaces
        assert f'{bib_format.indent}title = "myTitle"' in string
        assert f'{bib_format.indent}author = "myAuthor"' in string
        assert f'{bib_format.indent}veryverylongkeyfield = 2020' in string
    elif value_column == 10:
        assert f'{bib_format.indent}title   = "myTitle"' in string
        assert f'{bib_format.indent}author  = "myAuthor"' in string
        assert f'{bib_format.indent}veryverylongkeyfield = 2020' in string
    if value_column == "auto":
        assert f'{bib_format.indent}title                = "myTitle"' in string
        assert f'{bib_format.indent}author               = "myAuthor"' in string
        assert f'{bib_format.indent}veryverylongkeyfield = 2020' in string



def _dummy_entry():
    return Entry(
        entry_type="article",
        key="myKey",
        fields={
            "title": Field(key="title", value='"myTitle"'),
            "author": Field(key="author", value='"myAuthor"'),
        },
    )
