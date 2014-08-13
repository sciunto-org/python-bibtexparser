import unittest
from bibtexparser.bparser import BibTexParser


class TestHomogeniseFields(unittest.TestCase):
    def test_homogenise_default(self):
        with open('bibtexparser/tests/data/website.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            entries = bib.get_entry_list()
            self.assertIn('link', entries[0])
            self.assertNotIn('url', entries[0])

    def test_homogenise_on(self):
        with open('bibtexparser/tests/data/website.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), homogenise_fields=True)
            entries = bib.get_entry_list()
            self.assertIn('link', entries[0])
            self.assertNotIn('url', entries[0])

    def test_homogenise_off(self):
        with open('bibtexparser/tests/data/website.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), homogenise_fields=False)
            entries = bib.get_entry_list()
            self.assertNotIn('link', entries[0])
            self.assertIn('url', entries[0])
