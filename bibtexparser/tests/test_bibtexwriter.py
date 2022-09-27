# coding: utf-8
import tempfile
import unittest
import bibtexparser
from bibtexparser.bwriter import BibTexWriter, SortingStrategy
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

    def test_align_bool(self):
        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'abc123',
                                 'ENTRYTYPE': 'book',
                                 'author': 'test',
                                 'thisisaverylongkey': 'longvalue'}]
        writer = BibTexWriter()
        writer.align_values = True
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 author             = {test},
 thisisaverylongkey = {longvalue}
}
"""
        self.assertEqual(result, expected)

        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'veryveryverylongID',
                                 'ENTRYTYPE': 'book',
                                 'a': 'test',
                                 'bb': 'longvalue'}]
        writer = BibTexWriter()
        writer.align_values = True
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{veryveryverylongID,
 a  = {test},
 bb = {longvalue}
}
"""
        self.assertEqual(result, expected)

        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.contents = ['entries']
        writer.align_values = True
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{Toto3000,
 author    = {Toto, A and Titi, B},
 title     = {A title}
}

@article{Wigner1938,
 author    = {Wigner, E.},
 doi       = {10.1039/TF9383400029},
 issn      = {0014-7672},
 journal   = {Trans. Faraday Soc.},
 owner     = {fr},
 pages     = {29--41},
 publisher = {The Royal Society of Chemistry},
 title     = {The transition state method},
 volume    = {34},
 year      = {1938}
}

@book{Yablon2005,
 author    = {Yablon, A.D.},
 publisher = {Springer},
 title     = {Optical fiber fusion slicing},
 year      = {2005}
}
"""
        self.assertEqual(result, expected)

    def test_align_int(self):
        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'abc123',
                                 'ENTRYTYPE': 'book',
                                 'author': 'test',
                                 'thisisaverylongkey': 'longvalue'}]
        # Negative value should have no effect
        writer = BibTexWriter()
        writer.align_values = -20
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 author = {test},
 thisisaverylongkey = {longvalue}
}
"""
        self.assertEqual(result, expected)

        # Value smaller than longest field name should only impact the "short" field names
        writer = BibTexWriter()
        writer.align_values = 10
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 author     = {test},
 thisisaverylongkey = {longvalue}
}
"""
        self.assertEqual(result, expected)


        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.contents = ['entries']
        writer.align_values = 15
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{Toto3000,
 author          = {Toto, A and Titi, B},
 title           = {A title}
}

@article{Wigner1938,
 author          = {Wigner, E.},
 doi             = {10.1039/TF9383400029},
 issn            = {0014-7672},
 journal         = {Trans. Faraday Soc.},
 owner           = {fr},
 pages           = {29--41},
 publisher       = {The Royal Society of Chemistry},
 title           = {The transition state method},
 volume          = {34},
 year            = {1938}
}

@book{Yablon2005,
 author          = {Yablon, A.D.},
 publisher       = {Springer},
 title           = {Optical fiber fusion slicing},
 year            = {2005}
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

    def test_display_order(self):
        with open('bibtexparser/tests/data/multiple_entries_and_comments.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.contents = ['entries']
        writer.display_order = ['year', 'publisher', 'title']
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{Toto3000,
 title = {A title},
 author = {Toto, A and Titi, B}
}

@article{Wigner1938,
 year = {1938},
 publisher = {The Royal Society of Chemistry},
 title = {The transition state method},
 author = {Wigner, E.},
 doi = {10.1039/TF9383400029},
 issn = {0014-7672},
 journal = {Trans. Faraday Soc.},
 owner = {fr},
 pages = {29--41},
 volume = {34}
}

@book{Yablon2005,
 year = {2005},
 publisher = {Springer},
 title = {Optical fiber fusion slicing},
 author = {Yablon, A.D.}
}
"""
        self.assertEqual(result, expected)

    def test_align_multiline_values(self):
        with open('bibtexparser/tests/data/article_multilines.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.align_multiline_values = True
        writer.display_order = ["author", "title", "year", "journal", "abstract", "comments", "keyword"]
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@article{Cesar2013,
 author = {Jean César},
 title = {A mutline line title is very amazing. It should be
          long enough to test multilines... with two lines or should we
          even test three lines... What an amazing title.},
 year = {2013},
 journal = {Nice Journal},
 abstract = {This is an abstract. This line should be long enough to test
             multilines... and with a french érudit word},
 comments = {A comment},
 keyword = {keyword1, keyword2,
            multiline-keyword1, multiline-keyword2}
}
"""
        self.assertEqual(result, expected)

    def test_align_multiline_values_with_align(self):
        with open('bibtexparser/tests/data/article_multilines.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.align_multiline_values = True
        writer.align_values = True
        writer.display_order = ["author", "title", "year", "journal", "abstract", "comments", "keyword"]
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@article{Cesar2013,
 author   = {Jean César},
 title    = {A mutline line title is very amazing. It should be
             long enough to test multilines... with two lines or should we
             even test three lines... What an amazing title.},
 year     = {2013},
 journal  = {Nice Journal},
 abstract = {This is an abstract. This line should be long enough to test
             multilines... and with a french érudit word},
 comments = {A comment},
 keyword  = {keyword1, keyword2,
             multiline-keyword1, multiline-keyword2}
}
"""
        self.assertEqual(result, expected)

    def test_display_order_sorting(self):
        bib_database = BibDatabase()
        bib_database.entries = [{'ID': 'abc123',
                                 'ENTRYTYPE': 'book',
                                 'b': 'test2',
                                 'a': 'test1',
                                 'd': 'test4',
                                 'c': 'test3',
                                 'e': 'test5'}]
        # Only 'a' is not ordered. As it's only one element, strategy should not matter.
        for strategy in SortingStrategy:
            writer = BibTexWriter()
            writer.display_order = ['b', 'c', 'd', 'e', 'a']
            writer.display_order_sorting = strategy
            result = bibtexparser.dumps(bib_database, writer)
            expected = \
"""@book{abc123,
 b = {test2},
 c = {test3},
 d = {test4},
 e = {test5},
 a = {test1}
}
"""
            self.assertEqual(result, expected)

        # Test ALPHABETICAL_ASC strategy
        writer = BibTexWriter()
        writer.display_order = ['c']
        writer.display_order_sorting = SortingStrategy.ALPHABETICAL_ASC
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 c = {test3},
 a = {test1},
 b = {test2},
 d = {test4},
 e = {test5}
}
"""
        self.assertEqual(result, expected)

        # Test ALPHABETICAL_DESC strategy
        writer = BibTexWriter()
        writer.display_order = ['c']
        writer.display_order_sorting = SortingStrategy.ALPHABETICAL_DESC
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 c = {test3},
 e = {test5},
 d = {test4},
 b = {test2},
 a = {test1}
}
"""
        self.assertEqual(result, expected)

        # Test PRESERVE strategy
        writer = BibTexWriter()
        writer.display_order = ['c']
        writer.display_order_sorting = SortingStrategy.PRESERVE
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@book{abc123,
 c = {test3},
 b = {test2},
 a = {test1},
 d = {test4},
 e = {test5}
}
"""
        self.assertEqual(result, expected)

    def test_align_multiline_values_with_indent(self):
        with open('bibtexparser/tests/data/article_multilines.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.align_multiline_values = True
        writer.indent = ' ' * 3
        writer.display_order = ["author", "title", "year", "journal", "abstract", "comments", "keyword"]
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@article{Cesar2013,
   author = {Jean César},
   title = {A mutline line title is very amazing. It should be
            long enough to test multilines... with two lines or should we
            even test three lines... What an amazing title.},
   year = {2013},
   journal = {Nice Journal},
   abstract = {This is an abstract. This line should be long enough to test
               multilines... and with a french érudit word},
   comments = {A comment},
   keyword = {keyword1, keyword2,
              multiline-keyword1, multiline-keyword2}
}
"""
        self.assertEqual(result, expected)

    def test_align_multiline_values_with_align_with_indent(self):
        with open('bibtexparser/tests/data/article_multilines.bib') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)
        writer = BibTexWriter()
        writer.align_multiline_values = True
        writer.indent = ' ' * 3
        writer.align_values = True
        writer.display_order = ["author", "title", "year", "journal", "abstract", "comments", "keyword"]
        result = bibtexparser.dumps(bib_database, writer)
        expected = \
"""@article{Cesar2013,
   author   = {Jean César},
   title    = {A mutline line title is very amazing. It should be
               long enough to test multilines... with two lines or should we
               even test three lines... What an amazing title.},
   year     = {2013},
   journal  = {Nice Journal},
   abstract = {This is an abstract. This line should be long enough to test
               multilines... and with a french érudit word},
   comments = {A comment},
   keyword  = {keyword1, keyword2,
               multiline-keyword1, multiline-keyword2}
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
        expected = "@book{a\n}\n\n@article{b\n}\n\n@book{c\n}\n"
        self.assertEqual(result, expected)

    def test_sort_none(self):
        writer = BibTexWriter()
        writer.order_entries_by = None
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@article{b\n}\n\n@book{c\n}\n\n@book{a\n}\n"
        self.assertEqual(result, expected)

    def test_sort_id(self):
        writer = BibTexWriter()
        writer.order_entries_by = ('ID', )
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@book{a\n}\n\n@article{b\n}\n\n@book{c\n}\n"
        self.assertEqual(result, expected)

    def test_sort_type(self):
        writer = BibTexWriter()
        writer.order_entries_by = ('ENTRYTYPE', )
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@article{b\n}\n\n@book{c\n}\n\n@book{a\n}\n"
        self.assertEqual(result, expected)

    def test_sort_type_id(self):
        writer = BibTexWriter()
        writer.order_entries_by = ('ENTRYTYPE', 'ID')
        result = bibtexparser.dumps(self.bib_database, writer)
        expected = "@article{b\n}\n\n@book{a\n}\n\n@book{c\n}\n"
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
        expected = "@book{a\n}\n\n@article{b,\n year = {2000}\n}\n\n@book{c,\n year = {2010}\n}\n"
        self.assertEqual(result, expected)

    def test_unicode_problems(self):
        # See #51
        bibtex = """
        @article{Mesa-Gresa2013,
            abstract = {During a 4-week period half the mice (n = 16) were exposed to EE and the other half (n = 16) remained in a standard environment (SE). Aggr. Behav. 9999:XX-XX, 2013. © 2013 Wiley Periodicals, Inc.},
            author = {Mesa-Gresa, Patricia and P\'{e}rez-Martinez, Asunci\'{o}n and Redolat, Rosa},
            doi = {10.1002/ab.21481},
            file = {:Users/jscholz/Documents/mendeley/Mesa-Gresa, P\'{e}rez-Martinez, Redolat - 2013 - Environmental Enrichment Improves Novel Object Recognition and Enhances Agonistic Behavior.pdf:pdf},
            issn = {1098-2337},
            journal = {Aggressive behavior},
            month = "apr",
            number = {April},
            pages = {269--279},
            pmid = {23588702},
            title = {{Environmental Enrichment Improves Novel Object Recognition and Enhances Agonistic Behavior in Male Mice.}},
            url = {http://www.ncbi.nlm.nih.gov/pubmed/23588702},
            volume = {39},
            year = {2013}
        }
        """
        bibdb = bibtexparser.loads(bibtex)
        with tempfile.TemporaryFile(mode='w+', encoding="utf-8") as bibtex_file:
            bibtexparser.dump(bibdb, bibtex_file)
            # No exception should be raised

