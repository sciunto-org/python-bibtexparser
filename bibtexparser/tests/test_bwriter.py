#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

from __future__ import unicode_literals

import unittest
import os
import io
import sys

from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter, to_bibtex
from bibtexparser.customization import author


def _data_path(filename):
    return os.path.join('bibtexparser/tests/data', filename)


class TestBibtexWriterList(unittest.TestCase):

    def test_article(self):
        with io.open(_data_path('article.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('article_output.bib'), 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_article_with_annotation(self):
        with io.open(_data_path('article_with_annotation.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('article_with_annotation_output.bib'), 'r') \
                as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_book(self):
        with io.open(_data_path('book.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('book_output.bib'), 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_comma_first(self):
        with io.open(_data_path('book.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('book_comma_first.bib'), 'r') as bibfile:
            expected = bibfile.read()
        writer = BibTexWriter()
        writer.indent = '   '
        writer.comma_first = True
        result = writer.write(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_multiple(self):
        with io.open(_data_path('multiple_entries.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('multiple_entries_output.bib'), 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_exception_typeerror(self):
        with io.open(_data_path('article.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=author)
        self.assertRaises(TypeError, to_bibtex, bib)

    def test_with_strings(self):
        with io.open(_data_path('article_with_strings.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), common_strings=True,
                               interpolate_strings=False)
        with io.open(_data_path(
                'article_with_strings_output.bib'), 'r') as bibfile:
            expected = bibfile.read()
        result = to_bibtex(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_trailing_comma(self):
        with io.open(_data_path('article.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('article_trailing_comma_output.bib'), 'r') as bibfile:
            expected = bibfile.read()
        writer = BibTexWriter()
        writer.add_trailing_comma = True
        result = writer.write(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)

    def test_comma_first_and_trailing_comma(self):
        with io.open(_data_path('article.bib'), 'r') as bibfile:
            bib = BibTexParser(bibfile.read())

        with io.open(_data_path('article_comma_first_and_trailing_comma_output.bib'), 'r') as bibfile:
            expected = bibfile.read()
        writer = BibTexWriter()
        writer.add_trailing_comma = True
        writer.comma_first = True
        result = writer.write(bib)
        self.maxDiff = None
        self.assertEqual(expected, result)
