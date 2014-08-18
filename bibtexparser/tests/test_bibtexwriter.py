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
        bib_database.entries = [{'id': 'abc123',
                                 'type': 'book',
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
        bib_database.entries = [{'id': 'abc123',
                                 'type': 'book',
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