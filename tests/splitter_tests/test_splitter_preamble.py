import pytest

from bibtexparser.model import Preamble
from bibtexparser.splitter import Splitter
from tests.splitter_tests.resources import VALID_BIBTEX_SNIPPETS, PREAMBLES


@pytest.mark.parametrize("bibtex_before", VALID_BIBTEX_SNIPPETS)
@pytest.mark.parametrize("bibtex_after", VALID_BIBTEX_SNIPPETS)
@pytest.mark.parametrize("preamble_content", PREAMBLES)
def test_preamble_parsing(bibtex_before: str,
                          bibtex_after: str,
                          preamble_content: str):
    num_before = bibtex_before.lower().count("@preamble{")
    num_after = bibtex_after.lower().count("@preamble{")

    bibtex_str = bibtex_before + f"\n@preamble{{{preamble_content}}}\n" + bibtex_after

    library = Splitter(bibtex_str).split()

    assert len(library.preambles) == num_before + num_after + 1

    tested_preamble: Preamble = library.preambles[num_before]
    assert tested_preamble.value == preamble_content
    assert tested_preamble.raw == f"@preamble{{{preamble_content}}}"
    assert tested_preamble.start_line == bibtex_before.count("\n") + 1
