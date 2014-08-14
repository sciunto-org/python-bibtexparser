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

    def test_multiline_comments(self):
        with open('bibtexparser/tests/data/multiline_comments.bib') as bibfile:
            bib = BibTexParser(bibfile.read())
        expected = [
"""Lorem ipsum dolor sit amet,
consectetur adipisicing elit""",
"""
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident.
 ,
""",
"""


Sunt in culpa qui officia deserunt mollit anim id est laborum.


""",
""
        ]
        self.maxDiff = None
        self.assertEqual(bib.comments, expected)

    def test_multiple_entries(self):
        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibfile:
            bib = BibTexParser(bibfile.read())
        expected = ["",
                    "A comment"]
        self.assertEqual(bib.comments, expected)


class TestWriteComment(unittest.TestCase):
    def test_comment_write(self):
        with open('bibtexparser/tests/data/comments_only.bib') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/comments_only_output.bib') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.assertEqual(result, expected)

    def test_multiline_comment_write(self):
        with open('bibtexparser/tests/data/multiline_comments.bib') as bibfile:
            expected = bibfile.read()

        bib = BibTexParser(expected)
        result = to_bibtex(bib)
        self.assertEqual(result, expected)

    def test_multiple_entries(self):
        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibfile:
            bib = BibTexParser(bibfile.read())
        with open('bibtexparser/tests/data/multiple_entries_and_comments_output.bib') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.assertEqual(result, expected)
