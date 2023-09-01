"""Testing the parse_file function."""

import pytest

from bibtexparser import parse_file, writer


def test_gbk():
    library = parse_file("tests/resources/gbk_test.bib", encoding="gbk")
    assert library.entries[0]["author"] == "凯撒"
    assert library.entries[0]["title"] == "Test Title"
    assert library.entries[0]["year"] == "2013"
    assert library.entries[0]["journal"] == "测试期刊"
