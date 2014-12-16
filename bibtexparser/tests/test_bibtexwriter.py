import unittest
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


class TestBibTexWriter(unittest.TestCase):
    def test_content_entries_only(self):
        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.contents = ['entries']
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{Toto3000,
 author = {Toto, A and Titi, B},
 title = {A title}
}

@article{Wigner1938,
 author = {Wigner, E.},
 doi = {10.1039/TF9383400029},
 issn = {0014-7672},
 journal = {Trans. Faraday Soc.},
 owner = {fr},
 pages = {29--41},
 publisher = {The Royal Society of Chemistry},
 title = {The transition state method},
 volume = {34},
 year = {1938}
}

@book{Yablon2005,
 author = {Yablon, A.D.},
 publisher = {Springer},
 title = {Optical fiber fusion slicing},
 year = {2005}
}

"""
        self.assertEqual(result, expected)

    def test_content_comment_only(self):
        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.contents = ['comments']
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@comment{}

@comment{A comment}

"""
        self.assertEqual(result, expected)

    def test_indent(self):
        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'abc123',
                                 'ENTRYTYPE': 'book',
                                 'author': 'test'}]
        writer = BibTexWriter()
        writer.indent = '  '
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
  author = {test}
}

"""
        self.assertEqual(result, expected)

    def test_entry_separator(self):
        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'abc123',
                                 'ENTRYTYPE': 'book',
                                 'author': 'test'}]
        writer = BibTexWriter()
        writer.entry_separator = ''
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 author = {test}
}
"""
        self.assertEqual(result, expected)


class TestEntrySorting(unittest.TestCase):
    bib_database = BibDatabase()
    bib_database.entries = [{'ID': 'b',
                             'ENTRYTYPE': 'article'},
                            {'ID': 'c',
                             'ENTRYTYPE': 'book'},
                            {'ID': 'a',
                             'ENTRYTYPE': 'book'}]

    def test_sort_default(self):
        result = bibtexparser.dumps(self.bib_database)
        expected = "@book{a\n}\n\n@article{b\n}\n\n@book{c\n}\n\n"
        self.assertEqual(result, expected)

    def test_sort_none(self):
        writer = BibTexWriter()
        writer.order_entries_by = None
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@article{b\n}\n\n@book{c\n}\n\n@book{a\n}\n\n"
        self.assertEqual(result, expected)

    def test_sort_id(self):
        writer = BibTexWriter()
        writer.order_entries_by = ('ID', )
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@book{a\n}\n\n@article{b\n}\n\n@book{c\n}\n\n"
        self.assertEqual(result, expected)

    def test_sort_type(self):
        writer = BibTexWriter()
        writer.order_entries_by = ('ENTRYTYPE', )
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@article{b\n}\n\n@book{c\n}\n\n@book{a\n}\n\n"
        self.assertEqual(result, expected)

    def test_sort_type_id(self):
        writer = BibTexWriter()
        writer.order_entries_by = ('ENTRYTYPE', 'ID')
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@article{b\n}\n\n@book{a\n}\n\n@book{c\n}\n\n"
        self.assertEqual(result, expected)

    def test_sort_missing_field(self):
        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'b',
                                 'ENTRYTYPE': 'article',
                                 'year': '2000'},
                                {'ID': 'c',
                                 'ENTRYTYPE': 'book',
                                 'year': '2010'},
                                {'ID': 'a',
                                 'ENTRYTYPE': 'book'}]
        writer = BibTexWriter()
        writer.order_entries_by = ('year', )
        result = bibtexparser.dumps(bib_database, writer)
        expected = "@book{a\n}\n\n@article{b,\n year = {2000}\n}\n\n@book{c,\n year = {2010}\n}\n\n"
        self.assertEqual(result, expected)


