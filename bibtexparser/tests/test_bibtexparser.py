import unittest
import bibtexparser
from bibtexparser.bparser import BibTexParser
from tempfile import TemporaryFile


class TestBibtexParserParserMethods(unittest.TestCase):
    input_file_path = 'bibtexparser/tests/data/book.bib'
    entries_expected = [{'ENTRYTYPE': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'ID': 'Bird1987',
                         'volume': '1',
                         'title': 'Dynamics of Polymeric Liquid',
                         'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'
                        }]

    def test_parse_immediately(self):
        with open(self.input_file_path) as bibtex_file:
            bibtex_str = bibtex_file.read()
        bibtex_database = BibTexParser(bibtex_str)
        self.assertEqual(bibtex_database.entries, self.entries_expected)

    def test_parse_str(self):
        parser = BibTexParser()
        with open(self.input_file_path) as bibtex_file:
            bibtex_str = bibtex_file.read()
        bibtex_database = parser.parse(bibtex_str)
        self.assertEqual(bibtex_database.entries, self.entries_expected)

    def test_parse_file(self):
        parser = BibTexParser()
        with open(self.input_file_path) as bibtex_file:
            bibtex_database = parser.parse_file(bibtex_file)
        self.assertEqual(bibtex_database.entries, self.entries_expected)

    def test_parse_str_module(self):
        with open(self.input_file_path) as bibtex_file:
            bibtex_str = bibtex_file.read()
        bibtex_database = bibtexparser.loads(bibtex_str)
        self.assertEqual(bibtex_database.entries, self.entries_expected)

    def test_parse_file_module(self):
        with open(self.input_file_path) as bibtex_file:
            bibtex_database = bibtexparser.load(bibtex_file)
        self.assertEqual(bibtex_database.entries, self.entries_expected)


class TestBibtexparserWriteMethods(unittest.TestCase):
    input_file_path = 'bibtexparser/tests/data/book.bib'
    expected = \
"""@book{Bird1987,
 author = {Bird, R.B. and Armstrong, R.C. and Hassager, O.},
 edition = {2},
 publisher = {Wiley Edition},
 title = {Dynamics of Polymeric Liquid},
 volume = {1},
 year = {1987}
}

"""

    def test_write_str(self):
        with open(self.input_file_path) as bibtex_file:
            bibtex_database = bibtexparser.load(bibtex_file)
        result = bibtexparser.dumps(bibtex_database)
        self.assertEqual(result, self.expected)

    def test_write_file(self):
        with open(self.input_file_path) as bibtex_file:
            bibtex_database = bibtexparser.load(bibtex_file)

        with TemporaryFile(mode='w+') as bibtex_out_file:
            bibtexparser.dump(bibtex_database, bibtex_out_file)
            bibtex_out_file.seek(0)
            bibtex_out_str = bibtex_out_file.read()

        self.assertEqual(bibtex_out_str, self.expected)


if __name__ == '__main__':
    unittest.main()
