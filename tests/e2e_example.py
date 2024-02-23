from textwrap import dedent

import bibtexparser
from bibtexparser.middlewares.names import MergeCoAuthors
from bibtexparser.middlewares.names import MergeNameParts
from bibtexparser.middlewares.names import SeparateCoAuthors
from bibtexparser.middlewares.names import SplitNameParts

bibtex_string = dedent(
    """\
@article{Muller2020,
    title = "Some Paper Title",
    author = "John Muller and Jane Doe",
    journal = {Nature Reviews Materials},
    year = {2019}
}

@comment{
    This is a comment.
}

@preamble{e = mc^2}    """
)


def test_example():
    """A simplistic end-to-end parse-and-write example."""
    bib_database = bibtexparser.parse_string(
        bibtex_string,
        append_middleware=[
            SeparateCoAuthors(allow_inplace_modification=True),
            SplitNameParts(allow_inplace_modification=True),
        ],
    )

    new_bibtex_string = bibtexparser.write_string(
        bib_database,
        prepend_middleware=[
            MergeNameParts(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )

    # Note: As defaults change, this assertion may need to be updated.
    assert (
        new_bibtex_string.strip()
        == dedent(
            """
    @article{Muller2020,
    \ttitle = {Some Paper Title},
    \tauthor = {John Muller and Jane Doe},
    \tjournal = {Nature Reviews Materials},
    \tyear = {2019}
    }


    @comment{This is a comment.}


    @preamble{e = mc^2}"""
        ).strip()
    )
