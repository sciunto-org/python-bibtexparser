"""Testing the parse_file and write_file functions."""

import os
import tempfile

from bibtexparser import parse_file
from bibtexparser import write_file
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
