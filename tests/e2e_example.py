from textwrap import dedent

import pytest

import bibtexparser
from bibtexparser import parse_string
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.names import SeparateCoAuthors, SplitNameParts, MergeNameParts, MergeCoAuthors

bibtex_string = dedent("""\
@article{Muller2020,
    title = "Some Paper Title",
    author = "John Muller and Jane Doe",
    journal = {Nature Reviews Materials},
    year = {2019}
}

@comment{
    This is a comment.
}

@preamble{e = mc^2}    """)


@pytest.mark.skip("Writing is not yet implemented")  # TODO activate this example
def test_example():
    bib_database = bibtexparser.parse_string(bibtex_string,
                                             append_middleware=[
                                                 SeparateCoAuthors(allow_inplace_modification=True),
                                                 SplitNameParts(allow_inplace_modification=True),
                                             ])

    print(bib_database)

    new_bibtex_string = bibtexparser.write_string(bib_database,
                                                  append_middleware=[
                                                      MergeNameParts(allow_inplace_modification=True),
                                                      MergeCoAuthors(allow_inplace_modification=True),
                                                  ])
