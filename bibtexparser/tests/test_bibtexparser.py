#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *


def customizations_unicode(record):
    """Use all functions related to specific fields
    + converter to unicode.

    :param record: a record
    :returns: -- customized record
    """

    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    record = convert_to_unicode(record)
    return record

def customizations_latex(record):
    """Use all functions related to specific fields
    + converter to latex.

    :param record: a record
    :returns: -- customized record
    """

    record = homogeneize_latex_encoding(record)
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    return record

class TestBibtexParserList(unittest.TestCase):


    ###########
    # ARTICLE
    ###########
    def test_article(self):
        with open('bibtexparser/tests/data/article.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile)
            res = bib.get_entry_list()
            expected = [{'keyword': 'keyword1, keyword2',
                         'type': 'article',
                         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                         'year': '2013',
                         'journal': 'Nice Journal',
                         'id': 'Cesar2013',
                         'pages': '12-23',
                         'title': 'An amazing title',
                         'comments': 'A comment',
                         'author': 'Jean César',
                         'volume': '12',
                         'month': 'jan'
                         }]
        self.assertEqual(res, expected)

    def test_article_cust_unicode(self):
        with open('bibtexparser/tests/data/article.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile, customization=customizations_unicode)
            res = bib.get_entry_list()
        expected = [{'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                     'type': 'article',
                     'pages': '12--23',
                     'volume': '12',
                     'id': 'Cesar2013',
                     'year': '2013',
                     'author': ['César, Jean'],
                     'journal': {'id': 'NiceJournal', 'name': 'Nice Journal'},
                     'comments': 'A comment',
                     'month': 'jan',
                     'keyword': ['keyword1', 'keyword2'],
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_article_cust_latex(self):
        with open('bibtexparser/tests/data/article.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile, customization=customizations_latex)
            res = bib.get_entry_list()
        expected = [{'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french {\\\'e}rudit word',
                     'type': 'article',
                     'pages': '12--23',
                     'volume': '12',
                     'id': 'Cesar2013',
                     'year': '2013',
                     'author': ['C{\\\'e}sar, Jean'],
                     'journal': {'id': 'NiceJournal', 'name': 'Nice Journal'},
                     'comments': 'A comment',
                     'month': 'jan',
                     'keyword': ['keyword1', 'keyword2'],
                     'title': '{A}n amazing title'
                     }]
        self.assertEqual(res, expected)

    ###########
    # BOOK
    ###########
    def test_book(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile)
            res = bib.get_entry_list()
            expected = [{'type': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'id': 'Bird1987',
                         'volume': '1',
                         'title': 'Dynamics of Polymeric Liquid',
                         'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'
                         }]

        self.assertEqual(res, expected)

    def test_book_cust_unicode(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile, customization=customizations_unicode)
            res = bib.get_entry_list()
            expected = [{'type': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'id': 'Bird1987',
                         'volume': '1',
                         'title': 'Dynamics of Polymeric Liquid',
                         'author': ['Bird, R.B.', 'Armstrong, R.C.', 'Hassager, O.']
                         }]

        self.assertEqual(res, expected)

    def test_book_cust_latex(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile, customization=customizations_latex)
            res = bib.get_entry_list()
            expected = [{'type': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'id': 'Bird1987',
                         'volume': '1',
                         'title': '{D}ynamics of {P}olymeric {L}iquid',
                         'author': ['Bird, R.B.', 'Armstrong, R.C.', 'Hassager, O.']
                         }]

        self.assertEqual(res, expected)

    ###########
    # TRAPS
    ###########
    @unittest.skip('Parser is not able to make the difference between accent and end of field')
    def test_traps(self):
        with open('bibtexparser/tests/data/traps.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile)
            res = bib.get_entry_list()
            expected = [{'keyword': 'keyword1, keyword2',
                         'type': 'article',
                         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                         'year': '2013',
                         'journal': 'Nice Journal',
                         'id': 'Laide2013',
                         'pages': '12-23',
                         'title': 'An amazing title',
                         'comments': 'A comment',
                         'author': 'Jean Laid{\\\'e}, Ben Loaeb',
                         'volume': '12',
                         'month': 'jan'
                         }]
        self.assertEqual(res, expected)

if __name__ == '__main__':
    unittest.main()
