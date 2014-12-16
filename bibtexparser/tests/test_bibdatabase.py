import unittest
from bibtexparser.bibdatabase import BibDatabase


class TestBibDatabase(unittest.TestCase):
    entries = [{'ENTRYTYPE': 'book',
                'year': '1987',
                'edition': '2',
                'publisher': 'Wiley Edition',
                'ID': 'Bird1987',
                'volume': '1',
                'title': 'Dynamics of Polymeric Liquid',
                'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'
               }]

    def test_entries_list_method(self):
        bib_db = BibDatabase()
        bib_db.entries = self.entries
        self.assertEqual(bib_db.entries, bib_db.get_entry_list())

    def test_entries_dict_prop(self):
        bib_db = BibDatabase()
        bib_db.entries = self.entries
        self.assertEqual(bib_db.entries_dict, bib_db.get_entry_dict())


if __name__ == '__main__':
    unittest.main()
