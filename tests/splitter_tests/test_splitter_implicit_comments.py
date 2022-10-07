"""Tests the parsing of implicit comments, i.e., anything outside @{...} blocks."""
from textwrap import dedent

import pytest

from bibtexparser.library import Library
from bibtexparser.splitter import Splitter


def test_implicit_comment_eof():
    """Makes sure implicit comments at end of file are parsed."""

    bibtex_str = dedent("""\
    @article{article1, title={title1}}
    
    % This is an implicit comment at the end of the file.""")

    library = Splitter(bibtex_str).split()

    assert len(library.comments) == 1
    assert library.comments[0].comment == '% This is an implicit comment at the end of the file.'
    # Before applying the middleware, `comment` and `raw` are the same.
    assert library.comments[0].raw == '% This is an implicit comment at the end of the file.'
    assert library.comments[0].start_line == 2


def test_implicit_comment_start_of_file():
    """Makes sure implicit comments at start of file are parsed."""

    bibtex_str = ("This is an implicit comment at the start of the file.\n"
                  "@article{article1, title={title1}}")

    library = Splitter(bibtex_str).split()

    assert len(library.comments) == 1
    assert library.comments[0].comment == 'This is an implicit comment at the start of the file.'
    # Before applying the middleware, `comment` and `raw` are the same.
    assert library.comments[0].raw == 'This is an implicit comment at the start of the file.'
    assert library.comments[0].start_line == 0


@pytest.mark.parametrize("block", [
    "@article{article1, title={title1}}",
    "@article{article1, \n  title={title1}\n}",
    "@string{foo = \"bar\"}",
    "@preamble{e = mc^2}"
])
def test_implicit_comment_on_block_end_line(block):
    """Makes sure implicit comments on the same line as a closing `}` are parsed."""

    bibtex_str = f"{block}  My implicit comment"
    library: Library = Splitter(bibtex_str).split()
    assert len(library.comments) == 1
    assert library.comments[0].comment == 'My implicit comment'
    # Before applying the middleware, `comment` and `raw` are the same.
    assert library.comments[0].raw == 'My implicit comment'
    assert library.comments[0].start_line == bibtex_str.count('\n')


def test_multiline_implicit_comment():
    """Makes sure implicit comments spanning multiple lines are parsed."""

    bibtex_str = dedent("""\
    @article{article1, title={title1}}
    
    % This is an implicit comment
    %   spanning multiple lines
    
    with an empty line in between.
    
    @article{article2, title={title2}}""")

    library = Splitter(bibtex_str).split()

    assert len(library.comments) == 1

    expected_str = dedent("""\
    % This is an implicit comment
    %   spanning multiple lines
    
    with an empty line in between.""")
    assert library.comments[0].comment == expected_str
    # Before applying the middleware, `comment` and `raw` are the same.
    assert library.comments[0].raw == expected_str
    assert library.comments[0].start_line == 2
