# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io
import unittest
from bibtexparser.bparser import BibTexParser


class TestHomogenizeFields(unittest.TestCase):

    def test_homogenize_default(self):
        with open('bibtexparser/tests/data/website.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            entries = bib.get_entry_list()
            self.assertNotIn('url', entries[0])
            self.assertIn('link', entries[0])

    def test_homogenize_on(self):
        with open('bibtexparser/tests/data/website.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), homogenize_fields=True)
            entries = bib.get_entry_list()
            self.assertIn('url', entries[0])
            self.assertNotIn('link', entries[0])

    def test_homogenize_off(self):
        with open('bibtexparser/tests/data/website.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), homogenize_fields=False)
            entries = bib.get_entry_list()
            self.assertNotIn('url', entries[0])
            self.assertIn('link', entries[0])

    def test_homogenizes_fields(self):
        self.maxDiff = None
        with io.open('bibtexparser/tests/data/article_homogenize.bib',
                     'r', encoding='utf-8') as bibfile:
            bib = BibTexParser(bibfile.read(), homogenize_fields=True)
            expected_dict = {
                'Cesar2013': {
                    'keyword': 'keyword1, keyword2',
                    'ENTRYTYPE': 'article',
                    'abstract': 'This is an abstract. This line should be '
                                'long enough to test\nmultilines... and with '
                                'a french érudit word',
                    'year': '2013',
                    'journal': 'Nice Journal',
                    'ID': 'Cesar2013',
                    'pages': '12-23',
                    'title': 'An amazing title',
                    'comments': 'A comment',
                    'author': 'Jean César',
                    'volume': '12',
                    'month': 'jan',
                    'url': "http://my.link/to-content",
                    'subject': "Some topic of interest",
                    'editor': "Edith Or",
                }
            }
            self.assertEqual(bib.get_entry_dict(), expected_dict)
