#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

from __future__ import unicode_literals

import unittest
import sys

from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter, to_bibtex
from bibtexparser.customization import author


class TestBibtexWriterList(unittest.TestCase):

    ###########
    # ARTICLE
    ###########
    def test_article(self):
        with open('bibtexparser/tests/data/article.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/article_output.bib', 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        if not sys.version_info >= (3, 0):
            if isinstance(result, unicode):
                result = result.encode('utf-8')
        self.maxDiff = None
        self.assertEqual(expected, result)

    ###########
    # BOOK
    ###########
    def test_book(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/book_output.bib', 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    ###########
    # COMMA FIRST
    ###########
    def test_comma_first(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/book_comma_first.bib', 'r') as bibfile:
            expected = bibfile.read()
        writer = BibTexWriter()
        writer.indent = '   '
        writer.comma_first = True
        result = writer.write(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    ###########
    # PROTECT UPPER CASE
    ###########
    def test_protect_upper_case(self):
        with open('bibtexparser/tests/data/book2.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/book_protect_upper_case.bib', 'r') as bibfile:
            expected = bibfile.read()
        writer = BibTexWriter()
        writer.indent = '   '
        writer.protect_upper_case = True
        result = writer.write(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    @unittest.skip('Not implemented. If already in {}, should not add braces again')
    def test_protect_upper_case_alreadyprotected(self):
        with open('bibtexparser/tests/data/article_with_protection_braces.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/article_with_protection_braces.bib', 'r') as bibfile:
            expected = bibfile.read()
        writer = BibTexWriter()
        writer.indent = '   '
        writer.protect_upper_case = True
        result = writer.write(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)
    ###########
    # MULTIPLE
    ###########
    def test_multiple(self):
        with open('bibtexparser/tests/data/multiple_entries.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with open('bibtexparser/tests/data/multiple_entries_output.bib', 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    ###########
    # Exception
    ###########
    def test_exception_typeerror(self):
        with open('bibtexparser/tests/data/article.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=author)
        self.assertRaises(TypeError, to_bibtex, bib)

