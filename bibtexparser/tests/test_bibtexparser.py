#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import unittest
from bibtexparser.bibtexparser import getnames

class TestBibtexParserMethod(unittest.TestCase):

    def test_getnames(self):
        names = ['Foo Bar',
                 'F. Bar',
                 'Jean de Savigny',
                 'Jean la Tour',
                 #'Johannes Diderik van der Waals',
                 ]
        result = getnames(names)
        expected = ['Bar, Foo',
                    'Bar, F',
                    'de Savigny, Jean',
                    'la Tour, Jean',
                    #'van der Waals, Johannes Diderik',
                    ]
        self.assertEqual(result, expected)


from bibtexparser.bibtexparser import BibTexParser, customisations


class TestBibtexParser(unittest.TestCase):

    def test_article(self):
        with open('tests/data/article.bib', 'r') as bibfile:
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
        self.assert_equal(res, expected)

    #def test_article_cust(self):
    #bib = BibTexParser(bibfile, customisation=customisations)
    #print(bib.get_entry_list())
