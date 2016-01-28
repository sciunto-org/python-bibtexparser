
from __future__ import unicode_literals

import unittest
import sys

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

class TestArxivPdf(unittest.TestCase):
    # tests if arxiv_pdf in customization.py retrieves the correct
    # links to full pdf's on Arxiv as 'arxiv_pdf', if available

    input_file_path = 'data/arxiv_pdf.bib'
    entries_expected = [{'title': 'Quantum Copy-Protection and Quantum Money', 'year': '2009',
                         'author': 'Scott Aaronson', 'ID': 'Aar09', 'arxiv_pdf': 'http://arxiv.org/pdf/1110.5353v1',
                         'ENTRYTYPE': 'inproceedings'},
                        {'title': 'A simpler proof of existence of quantum weak coin flipping with arbitrarily small bias',
                         'year': '2014', 'author': 'Dorit Aharonov and Andr\\\'{e} Chailloux and Maor Ganz and '
                                                   'Iordanis Kerenidis and Lo\\"{i}ck Magnin',
                         'ID': 'ACG+14arxiv', 'arxiv_pdf': 'http://arxiv.org/pdf/1402.7166v1',
                         'ENTRYTYPE': 'misc'},
                        {'title': 'New Bounds for the Garden-Hose Model', 'year': '2014',
                         'author': 'Hartmut Klauck and Supartha Podder', 'ID': 'KP14',
                         'arxiv_pdf': 'http://arxiv.org/pdf/1412.4904v1', 'ENTRYTYPE': 'inproceedings'},
                        {'ID': 'Unruh2004', 'title': 'Simulatable security for quantum protocols',
                         'arxiv_pdf': 'http://arxiv.org/pdf/quant-ph/0409125v2', 'author': '{Unruh}, D.',
                         'ENTRYTYPE': 'misc'},
                        {'ID': 'dMM03', 'title': 'Experimental Quantum Computation and Information', 'year': '2003',
                         'author': 'F. de Martini and C. Monroe', 'ENTRYTYPE': 'book'}]

    def test_citation_key(self):
        with open(self.input_file_path) as bibtex_file:
            def key(record):
                record = arxiv_pdf(record)
                return record
            parser = BibTexParser()
            parser.customization = key
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
        self.assertEqual(bib_database.entries, self.entries_expected)

if __name__ == '__main__':
    unittest.main()
