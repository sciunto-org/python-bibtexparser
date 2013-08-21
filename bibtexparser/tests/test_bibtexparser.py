#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import unittest

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *


def customizations(record):
    """Use all functions

    :param record: a record
    :returns: -- customized record
    """

    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page(record)
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
                         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...',
                         'year': '2013',
                         'journal': 'Nice Journal',
                         'id': 'Cesar2013',
                         'pages': '12--23',
                         'title': 'An amazing title',
                         'comments': 'A comment',
                         'author': 'Jean César',
                         'volume': '12',
                         'month': 'jan'
                         }]
        self.assertEqual(res, expected)

    def test_article_cust(self):
        with open('bibtexparser/tests/data/article.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile, customization=customizations)
            res = bib.get_entry_list()
        expected = [{'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...',
                     'type': 'article',
                     'pages': '12 to 23',
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

    @unittest.skip('Bug on dot after letters')
    def test_book_cust(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile, customization=customizations)
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
