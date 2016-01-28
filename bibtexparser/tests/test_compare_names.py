import unittest
from bibtexparser.compare_names import *

class TestCompareNames(unittest.TestCase):
    def clean_authors(self):
        file = 'data/confusable_names.bib'
        cleaner = AuthorOrganizer(file)
        cleaner.take_longest_option = True
        cleaner.clean_authors()

    def read_output(self):
        with open('data/confusable_names_authors_cleaned.bib') as bibfile:
            output = bibfile.read()
        return output

    def test_comment_write(self):
        self.clean_authors()
        output = self.read_output()

        with open('data/confusable_names_output.bib') as bibfile:
            expected = bibfile.read()

        self.assertEqual(expected, output)
