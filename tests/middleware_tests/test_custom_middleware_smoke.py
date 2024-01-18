"""Smoke test for custom middleware, based on the #440 by @tdegeus"""

import bibtexparser
from bibtexparser.middlewares.middleware import BlockMiddleware

bibtex_str = """
@ARTICLE{Cesar2013,
  author = {Jean César and T. W. J. de Geus},
  title = {An amazing title},
  year = {2013},
  pages = {12--23},
  volume = {12},
  journal = {Nice Journal}
}
"""


abbreviations = {"Nice Journal": "NJ", "Another Nice Journal": "ANJ"}


class JournalAbbreviate(BlockMiddleware):
    def transform_entry(self, entry, *args, **kwargs):
        if entry["journal"] in abbreviations:
            entry["journal"] = abbreviations[entry["journal"]]
        return entry


def test_custom_middleware_smoke():
    """Test that the very simple custom middleware above works."""
    library = bibtexparser.parse_string(
        bibtex_str, append_middleware=[JournalAbbreviate(True)]
    )
    assert library.entries[0]["journal"] == "NJ"
