import unittest
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import to_bibtex


class TestParseComment(unittest.TestCase):
    def test_comment_count(self):
        with open('bibtexparser/tests/data/features.bib') as bibfile:
            bib = BibTexParser(bibfile.read())
            self.assertEqual(len(bib.comments), 3)

    def test_comment_list(self):
        with open('bibtexparser/tests/data/features.bib') as bibfile:
            bib = BibTexParser(bibfile.read())
            expected = ["ignore this line!",
                        "ignore this line too!",
                        "and ignore this line too!"]
            self.assertEqual(bib.comments, expected)