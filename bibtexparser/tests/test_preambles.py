import unittest
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from collections import OrderedDict


class TestPreambleParse(unittest.TestCase):
    def test_single_preamble_parse_count(self):
        bibtex_str = '@preamble{ a }\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        self.assertEqual(len(bib_database.preambles), 1)

    def test_multiple_preamble_parse_count(self):
        bibtex_str = '@preamble{ a }\n\n@preamble{b}\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        self.assertEqual(len(bib_database.preambles), 2)

    def test_single_preamble_parse(self):
        bibtex_str = '@preamble{ a }\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        expected = [' a ']
        self.assertEqual(bib_database.preambles, expected)

    def test_multiple_preamble_parse(self):
        bibtex_str = '@preamble{ a }\n\n@preamble{b}\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        expected = [' a ', 'b']
        self.assertEqual(bib_database.preambles, expected)


class TestPreambleWrite(unittest.TestCase):
    def test_single_preamble_write(self):
        bib_database = BibDatabase()
        bib_database.preambles = [' a ']
        result = bibtexparser.dumps(bib_database)
        expected = '@preamble{ a }\n\n'
        self.assertEqual(result, expected)

    def test_multiple_string_write(self):
        bib_database = BibDatabase()
        bib_database.preambles = [' a ', 'b']
        result = bibtexparser.dumps(bib_database)
        expected = '@preamble{ a }\n\n@preamble{b}\n\n'
        self.assertEqual(result, expected)