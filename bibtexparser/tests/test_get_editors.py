import unittest

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

class TestGetEditors(unittest.TestCase):
    input_file_path = 'data/find_editors.bib'
    entries_expected = [
        {'title': 'Generating hard instances of lattice problems',
         'author': 'M. Ajtai',
         'owner': 'chris',
         'year': '1996',
         'doi': '10.1145/237814.237838',
         '__markedentry': '[Barbara:1]',
         'editor': 'Gary L. Miller',
         'ID': 'Ajt96',
         'ENTRYTYPE': 'inproceedings',
         'booktitle': 'stoc96',
         'pages': '99--108',
         'timestamp': '2015.10.18'},
        {'title': 'Interactive Proofs For Quantum Computations',
         'archiveprefix': 'arXiv',
         'year': '2010',
         'editor': 'Andrew Chi-Chih Yao',
         '__markedentry': '[Barbara:1]',
         'arxivid': '0810.5375',
         'ID': 'ABE10',
         'owner': 'chris',
         'ENTRYTYPE': 'inproceedings',
         'author': 'Dorit Aharonov and Michael {Ben-Or} and Elad Eban',
         'booktitle': 'ics10',
         'pages': '453-469',
         'timestamp': '2015.10.18'},
        {'title': 'Approximating {ATSP} by Relaxing Connectivity',
         'author': 'Ola Svensson',
         'crossref': 'DBLP:conf/focs/2015',
         'bibsource': 'dblp computer science bibliography, http://dblp.org',
         'year': '2015',
         'doi': '10.1109/FOCS.2015.10',
         'editor': 'Venkatesan Guruswami',
         'ENTRYTYPE': 'inproceedings',
         'ID': 'DBLP:conf/focs/Svensson15',
         'biburl': 'http://dblp.uni-trier.de/rec/bib/conf/focs/Svensson15',
         'booktitle': '{IEEE} 56th Annual Symposium on Foundations of Computer Science, '
                      '{FOCS}\n2015, Berkeley, CA, USA, 17-20 October, 2015',
         'link': 'http://dx.doi.org/10.1109/FOCS.2015.10',
         'pages': '1--19',
         'timestamp': 'Mon, 04 Jan 2016 13:44:40 +0100'}]

    def test_citation_key(self):
        with open(self.input_file_path) as bibtex_file:
            def editors(record):
                record = get_editors(record)
                return record
            parser = BibTexParser()
            parser.customization = editors
            bib_database = bibtexparser.load(bibtex_file, parser=parser)

        self.assertEqual(bib_database.entries, self.entries_expected)

if __name__ == '__main__':
    unittest.main()
