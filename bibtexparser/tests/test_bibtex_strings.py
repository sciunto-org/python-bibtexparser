import unittest
import codecs
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
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



class TestStringWrite(unittest.TestCase):
    def test_single_string_write(self):
        bib_database = BibDatabase()
        bib_database.strings['name1'] = 'value1'
        result = bibtexparser.dumps(bib_database)
        expected = '@string{name1 = "value1"}\n\n'
        self.assertEqual(result, expected)

    def test_multiple_string_write(self):
        bib_database = BibDatabase()
        bib_database.strings['name1'] = 'value1'
        bib_database.strings['name2'] = 'value2'  # Order is important!
        result = bibtexparser.dumps(bib_database)
        expected = '@string{name1 = "value1"}\n\n@string{name2 = "value2"}\n\n'
        self.assertEqual(result, expected)
