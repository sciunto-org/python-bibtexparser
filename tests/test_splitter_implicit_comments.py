from bibtexparser.splitter import Splitter


def test_implicit_comment_eof():
    """Makes sure implicit comments at end of file are parsed."""

    bibtex_str = """@article{article1, title={title1}}
    
    % This is an implicit comment at the end of the file."""

    library = Splitter(bibtex_str).split()

    assert len(library.comments) == 1
    assert library.comments[0].comment == '% This is an implicit comment at the end of the file.'
    # Before applying the middleware, `comment` and `raw` are the same.
    assert library.comments[0].raw == '% This is an implicit comment at the end of the file.'
    assert library.comments[0].start_line == 2