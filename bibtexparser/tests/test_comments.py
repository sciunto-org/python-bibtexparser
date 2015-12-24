import unittest
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import to_bibtex


""" The code is supposed to treat comments the following way:
    Each @Comment opens a comment that ends when something
    that is not a comment is encountered. More precisely
    this means a line starting with an @. Lines that are not
    parsed as anything else are also considered comments.
    If the comment starts and ends with braces, they are removed.

    Current issues:
        - a comment followed by a line starting with @smthing
        that is not a valid bibtex element are parsed separately,
        that is as two comments.
        - braces are either ignored or removed which is not easily
        predictable.
"""


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
            bparser = BibTexParser()
            bib = bparser.parse_file(bibfile)
        expected = ["",
                    "A comment"]
        self.assertEqual(bib.comments, expected)

    def test_comments_percentage(self):
        with open('bibtexparser/tests/data/comments_percentage.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': 'Jean Cesar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Baltazar2013',
                     'year': '2013',
                     'author': 'Jean Baltazar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_comments_percentage_nocoma(self):
        with open('bibtexparser/tests/data/comments_percentage_nolastcoma.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': 'Jean Cesar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Baltazar2013',
                     'year': '2013',
                     'author': 'Jean Baltazar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_no_newline(self):
        comments = """This is a comment."""
        expected = ["This is a comment."]
        bib = BibTexParser(comments)
        self.assertEqual(bib.comments, expected)

    def test_43(self):
        comment = "@STRING{foo = \"bar\"}\n" \
                  "This is a comment\n" \
                  "This is a second comment."
        expected = "This is a comment\nThis is a second comment."
        bib = BibTexParser(comment)
        self.assertEqual(bib.comments, [expected])
        self.assertEqual(bib.strings, {'foo': 'bar'})

    def test_43_bis(self):
        comment = "@STRING{foo = \"bar\"}\n" \
                  "This is a comment\n" \
                  "STRING{Baz = \"This should be interpreted as comment.\"}"
        expected = "This is a comment\n" \
                   "STRING{Baz = \"This should be interpreted as comment.\"}"
        bib = BibTexParser(comment)
        self.assertEqual(bib.comments, [expected])
        self.assertEqual(bib.strings, {'foo': 'bar'})


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
