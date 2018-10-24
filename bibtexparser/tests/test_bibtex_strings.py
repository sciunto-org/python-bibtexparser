import io
import unittest
import codecs
import bibtexparser
from bibtexparser.bibdatabase import (BibDatabase, BibDataString,
                                      BibDataStringExpression)
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from collections import OrderedDict


class TestStringParse(unittest.TestCase):

    def test_single_string_parse_count(self):
        bibtex_str = '@string{name1 = "value1"}\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        self.assertEqual(len(bib_database.strings), 1)

    def test_multiple_string_parse_count(self):
        bibtex_str = '@string{name1 = "value1"}\n\n@string{name2 = "value2"}\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        self.assertEqual(len(bib_database.strings), 2)

    def test_single_string_parse(self):
        bibtex_str = '@string{name1 = "value1"}\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        expected = {'name1': 'value1'}
        self.assertEqual(bib_database.strings, expected)

    def test_multiple_string_parse(self):
        bibtex_str = '@string{name1 = "value1"}\n\n@string{name2 = "value2"}\n\n'
        bib_database = bibtexparser.loads(bibtex_str)
        expected = OrderedDict()
        expected['name1'] = 'value1'
        expected['name2'] = 'value2'
        self.assertEqual(bib_database.strings, expected)

    def test_string_braces(self):
        with codecs.open('bibtexparser/tests/data/string.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'author': 'Sang Kil Cha and Maverick Woo and David Brumley',
		     'ID': 'cha:oakland15',
		     'year': '2015',
		     'booktitle': 'Proceedings of the {IEEE} Symposium on Security and Privacy',
		     'title': '{Program-Adaptive Mutational Fuzzing}',
	             'ENTRYTYPE': 'inproceedings',
		     'pages': '725--741'
                     }]
        self.assertEqual(res, expected)

    def test_string_parse_accept_chars(self):
        bibtex_str = '@string{pub-ieee-std = {IEEE}}\n\n@string{pub-ieee-std:adr = {New York, NY, USA}}'
        bib_database = bibtexparser.loads(bibtex_str)
        self.assertEqual(len(bib_database.strings), 2)
        expected = OrderedDict()
        expected['pub-ieee-std'] = 'IEEE'
        expected['pub-ieee-std:adr'] = 'New York, NY, USA'
        self.assertEqual(bib_database.strings, expected)


class TestStringWrite(unittest.TestCase):

    def test_single_string_write(self):
        bib_database = BibDatabase()
        bib_database.strings['name1'] = 'value1'
        result = bibtexparser.dumps(bib_database)
        expected = '@string{name1 = {value1}}\n\n'
        self.assertEqual(result, expected)

    def test_multiple_string_write(self):
        bib_database = BibDatabase()
        bib_database.strings['name1'] = 'value1'
        bib_database.strings['name2'] = 'value2'  # Order is important!
        result = bibtexparser.dumps(bib_database)
        expected = '@string{name1 = {value1}}\n\n@string{name2 = {value2}}\n\n'
        self.assertEqual(result, expected)

    def test_ignore_common_strings(self):
        bib_database = BibDatabase()
        bib_database.load_common_strings()
        result = bibtexparser.dumps(bib_database)
        self.assertEqual(result, '')

    def test_ignore_common_strings_only_if_not_overloaded(self):
        bib_database = BibDatabase()
        bib_database.load_common_strings()
        bib_database.strings['jan'] = 'Janvier'
        result = bibtexparser.dumps(bib_database)
        self.assertEqual(result, '@string{jan = {Janvier}}\n\n')

    def test_write_common_strings(self):
        bib_database = BibDatabase()
        bib_database.load_common_strings()
        writer = BibTexWriter(write_common_strings=True)
        result = bibtexparser.dumps(bib_database, writer=writer)
        with io.open('bibtexparser/tests/data/common_strings.bib') as f:
            expected = f.read()
        self.assertEqual(result, expected)

    def test_write_dependent_strings(self):
        bib_database = BibDatabase()
        bib_database.strings['title'] = 'Mr'
        expr = BibDataStringExpression([BibDataString(bib_database, 'title'), 'Smith'])
        bib_database.strings['name'] = expr
        result = bibtexparser.dumps(bib_database)
        expected = '@string{title = {Mr}}\n\n@string{name = title # {Smith}}\n\n'
        self.assertEqual(result, expected)
