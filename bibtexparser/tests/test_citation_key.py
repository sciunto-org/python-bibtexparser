#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

from __future__ import unicode_literals

import unittest
import sys

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

class TestBibtexWriterList(unittest.TestCase):

    ###########################
    # MORE TESTS FOR:

    # ARXIV ENTRIES (?)
    # MULTIPLE ENTRIES IN 1 YEAR (?)
    ###########################

    input_file_path = 'data/citation_keys.bib'
    entries_expected = [
        {'alphakey': 'Cés13', 'year': '2013', 'ENTRYTYPE': 'article', 'ID': 'test1',
         'author': 'Jean César'},
        {'alphakey': 'Ćul99', 'ID': 'test2', 'ENTRYTYPE': 'article', 'year': '1999',
         'author': "{\\'C}ulafi{\\'c}, Dragana"},
        {'alphakey': 'MŽN+09', 'year': '2009', 'ENTRYTYPE': 'article', 'ID': 'test3',
         'author': "Miti{\\'c}-{\\'C}ulafi{\\'c}, Dragana and {\\v{Z}}egura, Bojana and "
                   "Nikoli{\\'c}, Biljana and Vukovi{\\'c}-Ga{\\v{c}}i{\\'c}, Branka and "
                   "Kne{\\v{z}}evi{\\'c}-Vuk{\\v{c}}evi{\\'c}, Jelena and "
                   "Filipi{\\v{c}}, Metka"},
        {'alphakey': 'vdBer09', 'year': '2009', 'ENTRYTYPE': 'inproceedings', 'ID': 'test4',
         'author': 'Abraham van der Berk'},
        {'alphakey': 'vdBA02', 'year': '2002', 'ENTRYTYPE': 'inproceedings', 'ID': 'test5',
         'author': 'Abraham van der Berk and Scott Aaronson'},
        {'alphakey': 'Aar09', 'year': '2009', 'ENTRYTYPE': 'inproceedings', 'ID': 'test6',
         'author': 'Scott Aaronson'},
        {'alphakey': 'AFG+12', 'year': '2012', 'ENTRYTYPE': 'article', 'ID': 'test7',
         'author': 'Scott Aaronson and Ewdard Farhi and David Gosset '
                   'and Avinatan Hassidim and Jonathan Kelner and Andrew Lutomirski'},
        {'alphakey': 'LMvdP13', 'year': '2013', 'ENTRYTYPE': 'inproceedings', 'ID': 'test8',
         'author': 'Laarhoven, Thijs and Mosca, Michele and van de Pol, Joop'},
        {'alphakey': 'vDam13', 'year': '2013', 'ENTRYTYPE': 'article', 'ID': 'test9',
         'author': 'van Dam, Wim'}]

    def test_citation_key(self):
        with open(self.input_file_path) as bibtex_file:
            def key(record):
                record = citation_key(record)
                return record
            parser = BibTexParser()
            parser.customization = key
            bib_database = bibtexparser.load(bibtex_file, parser=parser)

        self.assertEqual(bib_database.entries, self.entries_expected)

if __name__ == '__main__':
    unittest.main()
