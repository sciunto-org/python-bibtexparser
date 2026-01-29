"""Testing the parse_file and write_file functions."""

import os
import tempfile
import warnings

import pytest

from bibtexparser import parse_file
from bibtexparser import write_file
from bibtexparser import write_string
from bibtexparser.library import Library
from bibtexparser.model import Entry
from bibtexparser.model import Field


def test_gbk():
    library = parse_file("tests/resources/gbk_test.bib", encoding="gbk")
    assert library.entries[0]["author"] == "凯撒"
    assert library.entries[0]["title"] == "Test Title"
    assert library.entries[0]["year"] == "2013"
    assert library.entries[0]["journal"] == "测试期刊"


def test_write_file_default_encoding():
    """Test write_file uses UTF-8 by default."""
    entry = Entry(
        entry_type="article",
        key="test2024",
        fields=[
            Field(key="author", value="Müller"),
            Field(key="title", value="Ångström measurements"),
        ],
    )
    library = Library([entry])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        write_file(temp_path, library)
        # Read back and verify
        with open(temp_path, encoding="UTF-8") as f:
            content = f.read()
        assert "Müller" in content
        assert "Ångström" in content
    finally:
        os.unlink(temp_path)


def test_write_file_gbk_encoding():
    """Test write_file with GBK encoding for Chinese characters."""
    entry = Entry(
        entry_type="article",
        key="test2024",
        fields=[
            Field(key="author", value="凯撒"),
            Field(key="title", value="Test Title"),
            Field(key="journal", value="测试期刊"),
        ],
    )
    library = Library([entry])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        write_file(temp_path, library, encoding="gbk")
        # Read back with GBK and verify
        with open(temp_path, encoding="gbk") as f:
            content = f.read()
        assert "凯撒" in content
        assert "测试期刊" in content
    finally:
        os.unlink(temp_path)


def test_write_file_roundtrip_gbk():
    """Test round-trip: parse GBK file, write with GBK, parse again."""
    # Parse original GBK file
    library = parse_file("tests/resources/gbk_test.bib", encoding="gbk")
    original_author = library.entries[0]["author"]
    original_journal = library.entries[0]["journal"]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        # Write with GBK encoding
        write_file(temp_path, library, encoding="gbk")
        # Parse back
        library2 = parse_file(temp_path, encoding="gbk")
        assert library2.entries[0]["author"] == original_author
        assert library2.entries[0]["journal"] == original_journal
    finally:
        os.unlink(temp_path)


# Deprecation warning tests for write_file and write_string
def test_write_file_deprecated_parse_stack_parameter():
    """Test that using deprecated 'parse_stack' parameter issues a warning."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            write_file(temp_path, library, parse_stack=[])
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "parse_stack" in str(w[0].message)
            assert "unparse_stack" in str(w[0].message)
    finally:
        os.unlink(temp_path)


def test_write_file_deprecated_append_middleware_parameter():
    """Test that using deprecated 'append_middleware' parameter issues a warning."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            write_file(temp_path, library, append_middleware=[])
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "append_middleware" in str(w[0].message)
            assert "prepend_middleware" in str(w[0].message)
    finally:
        os.unlink(temp_path)


def test_write_file_both_parse_stack_and_unparse_stack_raises_error():
    """Test that providing both parse_stack and unparse_stack raises ValueError."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as excinfo:
            write_file(temp_path, library, parse_stack=[], unparse_stack=[])
        assert "parse_stack" in str(excinfo.value)
        assert "unparse_stack" in str(excinfo.value)
        assert "Use 'unparse_stack' instead" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_write_file_both_append_and_prepend_middleware_raises_error():
    """Test that providing both append_middleware and prepend_middleware raises ValueError."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as excinfo:
            write_file(temp_path, library, append_middleware=[], prepend_middleware=[])
        assert "append_middleware" in str(excinfo.value)
        assert "prepend_middleware" in str(excinfo.value)
        assert "Use 'prepend_middleware' instead" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_write_file_unexpected_keyword_argument_raises_error():
    """Test that unexpected keyword arguments raise TypeError."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(TypeError) as excinfo:
            write_file(temp_path, library, unknown_param="value")
        assert "unexpected keyword arguments" in str(excinfo.value)
        assert "unknown_param" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_write_string_deprecated_parse_stack_parameter():
    """Test that using deprecated 'parse_stack' parameter issues a warning."""
    library = Library([])

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        write_string(library, parse_stack=[])
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "parse_stack" in str(w[0].message)
        assert "unparse_stack" in str(w[0].message)


def test_write_string_deprecated_append_middleware_parameter():
    """Test that using deprecated 'append_middleware' parameter issues a warning."""
    library = Library([])

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        write_string(library, append_middleware=[])
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "append_middleware" in str(w[0].message)
        assert "prepend_middleware" in str(w[0].message)


def test_write_string_both_parse_stack_and_unparse_stack_raises_error():
    """Test that providing both parse_stack and unparse_stack raises ValueError."""
    library = Library([])

    with pytest.raises(ValueError) as excinfo:
        write_string(library, parse_stack=[], unparse_stack=[])
    assert "parse_stack" in str(excinfo.value)
    assert "unparse_stack" in str(excinfo.value)
    assert "Use 'unparse_stack' instead" in str(excinfo.value)


def test_write_string_both_append_and_prepend_middleware_raises_error():
    """Test that providing both append_middleware and prepend_middleware raises ValueError."""
    library = Library([])

    with pytest.raises(ValueError) as excinfo:
        write_string(library, append_middleware=[], prepend_middleware=[])
    assert "append_middleware" in str(excinfo.value)
    assert "prepend_middleware" in str(excinfo.value)
    assert "Use 'prepend_middleware' instead" in str(excinfo.value)


def test_write_string_unexpected_keyword_argument_raises_error():
    """Test that unexpected keyword arguments raise TypeError."""
    library = Library([])

    with pytest.raises(TypeError) as excinfo:
        write_string(library, unknown_param="value")
    assert "unexpected keyword arguments" in str(excinfo.value)
    assert "unknown_param" in str(excinfo.value)
