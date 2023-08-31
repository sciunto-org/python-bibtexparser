"""Testing the parse_file function."""

import pytest

from bibtexparser import parse_file,writer

def test_gbk():
    library=parse_file("tests/gbk_test.bib",encoding="gbk")
    lines=writer.write(library).splitlines()
    assert len(lines)==6
    assert lines[0]=='@article{凯撒2013,'
    assert lines[1]=='\tauthor = 凯撒,'
    assert lines[2]=='\ttitle = Test Title,'
    assert lines[3]=='\tyear = 2013,'
    assert lines[4]=='\tjournal = 测试期刊'
    assert lines[5]=='}'
