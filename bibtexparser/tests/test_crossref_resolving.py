import unittest2 as unittest
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser


class TestCrossRef(unittest.TestCase):
    def test_crossref(self):
        self.maxDiff = None
        input_file_path = 'bibtexparser/tests/data/crossref_entries.bib'
        entries_expected = {'cr1': {'ENTRYTYPE': 'inbook',
                                    'ID': 'cr1',
                                    '_FROM_CROSSREF': ['editor', 'publisher', 'year'],
                                    'archiveprefix': 'SomEPrFiX',
                                    'author': 'Graham Gullam',
                                    'crossref': 'cr_m',
                                    'editor': 'Edgar Erbriss',
                                    'origdate': '1955',
                                    'primaryclass': 'SOMECLASS',
                                    'publisher': 'Grimble',
                                    'title': 'Great and Good Graphs',
                                    'year': '1974'},
                            'cr2': {'ENTRYTYPE': 'inbook',
                                    'ID': 'cr2',
                                    '_FROM_CROSSREF': ['editor', 'publisher', 'year'],
                                    'author': 'Frederick Fumble',
                                    'crossref': 'cr_m',
                                    'editor': 'Edgar Erbriss',
                                    'institution': 'Institution',
                                    'origdate': '1943',
                                    'publisher': 'Grimble',
                                    'school': 'School',
                                    'title': 'Fabulous Fourier Forms',
                                    'year': '1974'},
                            'cr3': {'ENTRYTYPE': 'inbook',
                                    'ID': 'cr3',
                                    '_FROM_CROSSREF': ['editor', 'publisher', 'year'],
                                    'archiveprefix': 'SomEPrFiX',
                                    'author': 'Arthur Aptitude',
                                    'crossref': 'crt',
                                    'editor': 'Mark Monkley',
                                    'eprinttype': 'sometype',
                                    'origdate': '1934',
                                    'publisher': 'Rancour',
                                    'title': 'Arrangements of All Articles',
                                    'year': '1996'},
                            'cr4': {'ENTRYTYPE': 'inbook',
                                    'ID': 'cr4',
                                    '_FROM_CROSSREF': ['editor', 'publisher', 'year'],
                                    'author': 'Morris Mumble',
                                    'crossref': 'crn',
                                    'editor': 'Jeremy Jermain',
                                    'origdate': '1911',
                                    'publisher': 'Pillsbury',
                                    'title': 'Enterprising Entities',
                                    'year': '1945'},
                            'cr5': {'ENTRYTYPE': 'inbook',
                                    'ID': 'cr5',
                                    '_FROM_CROSSREF': ['editor', 'publisher', 'year'],
                                    'author': 'Oliver Ordinary',
                                    'crossref': 'crn',
                                    'editor': 'Jeremy Jermain',
                                    'origdate': '1919',
                                    'publisher': 'Pillsbury',
                                    'title': 'Questionable Quidities',
                                    'year': '1945'},
                            'cr6': {'ENTRYTYPE': 'inproceedings',
                                    'ID': 'cr6',
                                    '_FROM_CROSSREF': ['address',
                                                       'editor',
                                                       'eventdate',
                                                       'eventtitle',
                                                       'publisher',
                                                       'venue'],
                                    'address': 'Address',
                                    'author': 'Author, Firstname',
                                    'booktitle': 'Manual booktitle',
                                    'crossref': 'cr6i',
                                    'editor': 'Editor',
                                    'eventdate': '2009-08-21/2009-08-24',
                                    'eventtitle': 'Title of the event',
                                    'pages': '123--',
                                    'publisher': 'Publisher of proceeding',
                                    'title': 'Title of inproceeding',
                                    'venue': 'Location of event',
                                    'year': '2009'},
                            'cr6i': {'ENTRYTYPE': 'proceedings',
                                     'ID': 'cr6i',
                                     'address': 'Address',
                                     'author': 'Spurious Author',
                                     'editor': 'Editor',
                                     'eventdate': '2009-08-21/2009-08-24',
                                     'eventtitle': 'Title of the event',
                                     'publisher': 'Publisher of proceeding',
                                     'title': 'Title of proceeding',
                                     'venue': 'Location of event',
                                     'year': '2009'},
                            'cr7': {'ENTRYTYPE': 'inbook',
                                    'ID': 'cr7',
                                    '_FROM_CROSSREF': ['publisher', 'subtitle', 'titleaddon', 'verba'],
                                    'author': 'Author, Firstname',
                                    'crossref': 'cr7i',
                                    'pages': '123--126',
                                    'publisher': 'Publisher of proceeding',
                                    'subtitle': 'Book Subtitle',
                                    'title': 'Title of Book bit',
                                    'titleaddon': 'Book Titleaddon',
                                    'verba': 'String',
                                    'year': '2010'},
                            'cr7i': {'ENTRYTYPE': 'book',
                                     'ID': 'cr7i',
                                     'author': 'Brian Bookauthor',
                                     'publisher': 'Publisher of proceeding',
                                     'subtitle': 'Book Subtitle',
                                     'title': 'Book Title',
                                     'titleaddon': 'Book Titleaddon',
                                     'verba': 'String',
                                     'year': '2009'},
                            'cr8': {'ENTRYTYPE': 'incollection',
                                    'ID': 'cr8',
                                    '_FROM_CROSSREF': ['editor', 'publisher', 'subtitle', 'titleaddon'],
                                    'author': 'Smith, Firstname',
                                    'crossref': 'cr8i',
                                    'editor': 'Brian Editor',
                                    'pages': '1--12',
                                    'publisher': 'Publisher of Collection',
                                    'subtitle': 'Book Subtitle',
                                    'title': 'Title of Collection bit',
                                    'titleaddon': 'Book Titleaddon',
                                    'year': '2010'},
                            'cr8i': {'ENTRYTYPE': 'collection',
                                     'ID': 'cr8i',
                                     'editor': 'Brian Editor',
                                     'publisher': 'Publisher of Collection',
                                     'subtitle': 'Book Subtitle',
                                     'title': 'Book Title',
                                     'titleaddon': 'Book Titleaddon',
                                     'year': '2009'},
                            'cr_m': {'ENTRYTYPE': 'book',
                                     'ID': 'cr_m',
                                     'editor': 'Edgar Erbriss',
                                     'publisher': 'Grimble',
                                     'title': 'Graphs of the Continent',
                                     'year': '1974'},
                            'crn': {'ENTRYTYPE': 'book',
                                    'ID': 'crn',
                                    'editor': 'Jeremy Jermain',
                                    'publisher': 'Pillsbury',
                                    'title': 'Vanquished, Victor, Vandal',
                                    'year': '1945'},
                            'crt': {'ENTRYTYPE': 'book',
                                    'ID': 'crt',
                                    'editor': 'Mark Monkley',
                                    'publisher': 'Rancour',
                                    'title': 'Beasts of the Burbling Burns',
                                    'year': '1996'}}
        parser = BibTexParser(add_missing_from_crossref=True, ignore_nonstandard_types=False)
        with open(input_file_path) as bibtex_file:
            bibtex_database = parser.parse_file(bibtex_file)
        self.assertDictEqual(bibtex_database.entries_dict, entries_expected)

    def test_crossref_cascading(self):
        input_file_path = 'bibtexparser/tests/data/crossref_cascading.bib'
        entries_expected = {'r1': {'ENTRYTYPE': 'book',
                                   'ID': 'r1',
                                   '_FROM_CROSSREF': [],
                                   'crossref': 'r2',
                                   'date': '1911'},
                            'r2': {'ENTRYTYPE': 'book',
                                   'ID': 'r2',
                                   '_FROM_CROSSREF': [],
                                   'crossref': 'r3',
                                   'date': '1911'},
                            'r3': {'ENTRYTYPE': 'book',
                                   'ID': 'r3',
                                   '_FROM_CROSSREF': [],
                                   'crossref': 'r4',
                                   'date': '1911'},
                            'r4': {'ENTRYTYPE': 'book',
                                   'ID': 'r4',
                                   'date': '1911'}}

        parser = BibTexParser(add_missing_from_crossref=True)
        with open(input_file_path) as bibtex_file:
            bibtex_database = parser.parse_file(bibtex_file)
        self.assertDictEqual(bibtex_database.entries_dict, entries_expected)

    def test_crossref_cascading_cycle(self):
        input_file_path = 'bibtexparser/tests/data/crossref_cascading_cycle.bib'
        entries_expected = {'circ1': {'ENTRYTYPE': 'book',
                                      'ID': 'circ1',
                                      '_FROM_CROSSREF': [],
                                      'crossref': 'circ2',
                                      'date': '1911'},
                            'circ2': {'ENTRYTYPE': 'book',
                                      'ID': 'circ2',
                                      '_FROM_CROSSREF': [],
                                      'crossref': 'circ1',
                                      'date': '1911'}}
        parser = BibTexParser(add_missing_from_crossref=True)
        with self.assertLogs('bibtexparser.bibdatabase', level='ERROR') as cm:
            with open(input_file_path) as bibtex_file:
                bibtex_database = parser.parse_file(bibtex_file)
            self.assertIn("ERROR:bibtexparser.bibdatabase:Circular crossref dependency: circ1->circ2->circ1.", cm.output)
        self.assertDictEqual(bibtex_database.entries_dict, entries_expected)

    def test_crossref_missing_entries(self):
        input_file_path = 'bibtexparser/tests/data/crossref_missing_entries.bib'
        entries_expected = {'mcr': {'ENTRYTYPE': 'inbook',
                                    'ID': 'mcr',
                                    '_crossref': 'missing1',
                                    'author': 'Megan Mistrel',
                                    'crossref': 'missing1',
                                    'origdate': '1933',
                                    'title': 'Lumbering Lunatics'}}

        parser = BibTexParser(add_missing_from_crossref=True)
        with self.assertLogs('bibtexparser.bibdatabase', level='ERROR') as cm:
            with open(input_file_path) as bibtex_file:
                bibtex_database = parser.parse_file(bibtex_file)
            self.assertIn("ERROR:bibtexparser.bibdatabase:Crossref reference missing1 for mcr is missing.", cm.output)
        self.assertDictEqual(bibtex_database.entries_dict, entries_expected)

if __name__ == '__main__':
    unittest.main()
