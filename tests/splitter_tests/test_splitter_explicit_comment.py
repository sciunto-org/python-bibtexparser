import pytest

from bibtexparser.model import ExplicitComment
from bibtexparser.splitter import Splitter
from tests.resources import EDGE_CASE_VALUES
from tests.resources import VALID_BIBTEX_SNIPPETS


@pytest.mark.parametrize("bibtex_before", VALID_BIBTEX_SNIPPETS)
@pytest.mark.parametrize("bibtex_after", VALID_BIBTEX_SNIPPETS)
@pytest.mark.parametrize("comment_content", EDGE_CASE_VALUES)
def test_explicit_comment_parsing(bibtex_before: str, bibtex_after: str, comment_content: str):
    num_before_comments = bibtex_before.lower().count("@comment{")
    num_after_comments = bibtex_after.lower().count("@comment{")

    bibtex_str = bibtex_before + f"\n@comment{{{comment_content}}}\n" + bibtex_after

    library = Splitter(bibtex_str).split()
    explicit_comments = [c for c in library.comments if isinstance(c, ExplicitComment)]

    assert len(explicit_comments) == num_before_comments + num_after_comments + 1

    tested_comment = explicit_comments[num_before_comments]
    assert tested_comment.comment == comment_content
    assert tested_comment.raw == f"@comment{{{comment_content}}}"
    assert tested_comment.start_line == bibtex_before.count("\n") + 1
