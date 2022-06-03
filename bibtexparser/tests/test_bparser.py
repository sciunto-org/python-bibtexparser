#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest
import codecs

from bibtexparser.bparser import BibTexParser
from bibtexparser.bibdatabase import (COMMON_STRINGS, BibDataStringExpression)
from bibtexparser.customization import *
from bibtexparser import customization


def customizations_unicode(record):
    """Use all functions related to specific fields
    + converter to unicode.

    :param record: a record
    :returns: -- customized record
    """

    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    record = convert_to_unicode(record)
    return record


def customizations_latex(record):
    """Use all functions related to specific fields
    + converter to latex.

    :param record: a record
    :returns: -- customized record
    """

    record = homogenize_latex_encoding(record)
    record = type(record)
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    return record


class TestBibtexParserList(unittest.TestCase):

    def test_empty_string(self):
        bib = BibTexParser("")
        self.assertEqual(bib.entries, [])
        self.assertEqual(bib.comments, [])
        self.assertEqual(bib.preambles, [])
        self.assertEqual(bib.strings, {})

    ###########
    # ARTICLE
    ###########
    # test also that list and dict are equivalent
    def test_article(self):
        with codecs.open('bibtexparser/tests/data/article.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
            res_list = bib.get_entry_list()
            res_dict = bib.get_entry_dict()
            expected_list = [{'keyword': 'keyword1, keyword2',
                              'ENTRYTYPE': 'article',
                              'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                              'year': '2013',
                              'journal': 'Nice Journal',
                              'ID': 'Cesar2013',
                              'pages': '12-23',
                              'title': 'An amazing title',
                              'comments': 'A comment',
                              'author': 'Jean César',
                              'volume': '12',
                              'month': 'jan'
                              }]
            expected_dict = {'Cesar2013': {'keyword': 'keyword1, keyword2',
                              'ENTRYTYPE': 'article',
                              'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                              'year': '2013',
                              'journal': 'Nice Journal',
                              'ID': 'Cesar2013',
                              'pages': '12-23',
                              'title': 'An amazing title',
                              'comments': 'A comment',
                              'author': 'Jean César',
                              'volume': '12',
                              'month': 'jan'
                              }}
        self.assertEqual(res_list, expected_list)
        self.assertEqual(res_dict, expected_dict)

    def test_article_annotation(self):
        with codecs.open('bibtexparser/tests/data/article_with_annotation.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
            res_list = bib.get_entry_list()
            res_dict = bib.get_entry_dict()
            expected_list = [{'keyword': 'keyword1, keyword2',
                              'ENTRYTYPE': 'article',
                              'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                              'year': '2013',
                              'journal': 'Nice Journal',
                              'ID': 'Cesar2013',
                              'pages': '12-23',
                              'title': 'An amazing title',
                              'comments': 'A comment',
                              'author': 'Jean César',
                              'author+an': '1=highlight',
                              'volume': '12',
                              'month': 'jan'
                              }]
            expected_dict = {'Cesar2013': {'keyword': 'keyword1, keyword2',
                                           'ENTRYTYPE': 'article',
                                           'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                                           'year': '2013',
                                           'journal': 'Nice Journal',
                                           'ID': 'Cesar2013',
                                           'pages': '12-23',
                                           'title': 'An amazing title',
                                           'comments': 'A comment',
                                           'author': 'Jean César',
                                           'author+an': '1=highlight',
                                           'volume': '12',
                                           'month': 'jan'
                                           }}
        self.assertEqual(res_list, expected_list)
        self.assertEqual(res_dict, expected_dict)

    def test_article_start_bom(self):
        with codecs.open('bibtexparser/tests/data/article_start_with_bom.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                     'ENTRYTYPE': 'article',
                     'pages': '12-23',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': 'Jean César',
                     'journal': 'Nice Journal',
                     'comments': 'A comment',
                     'month': 'jan',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_article_cust_unicode(self):
        with codecs.open('bibtexparser/tests/data/article.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=customizations_unicode)
            res = bib.get_entry_list()
        expected = [{'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                     'ENTRYTYPE': 'article',
                     'pages': '12--23',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': ['César, Jean'],
                     'journal': {'ID': 'NiceJournal', 'name': 'Nice Journal'},
                     'comments': 'A comment',
                     'month': 'jan',
                     'keyword': ['keyword1', 'keyword2'],
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_article_cust_latex(self):
        with codecs.open('bibtexparser/tests/data/article.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=customizations_latex)
            res = bib.get_entry_list()
        expected = [{'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french {\\\'e}rudit word',
                     'ENTRYTYPE': 'article',
                     'pages': '12--23',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': ['C{\\\'e}sar, Jean'],
                     'journal': {'ID': 'NiceJournal', 'name': 'Nice Journal'},
                     'comments': 'A comment',
                     'month': 'jan',
                     'keyword': ['keyword1', 'keyword2'],
                     'title': '{A}n amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_article_cust_order(self):
        def cust(record):
            record = customization.page_double_hyphen(record)
            record = customization.homogenize_latex_encoding(record)
            record = customization.author(record)
            return record

        def cust2(record):
            record = customization.author(record)
            record = customization.page_double_hyphen(record)
            record = customization.homogenize_latex_encoding(record)
            return record

        with open('bibtexparser/tests/data/multiple_entries.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=cust)
            res = bib.get_entry_list()
        with open('bibtexparser/tests/data/multiple_entries.bib', 'r') as bibfile:
            bib2 = BibTexParser(bibfile.read(), customization=cust2)
            res2 = bib.get_entry_list()
        self.assertEqual(res, res2)

    def test_article_missing_coma(self):
        with open('bibtexparser/tests/data/article_missing_coma.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': 'Jean Cesar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Baltazar2013',
                     'year': '2013',
                     'author': 'Jean Baltazar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Aimar2013',
                     'year': '2013',
                     'author': 'Jean Aimar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title',
                     'month': 'january'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Doute2013',
                     'year': '2013',
                     'author': 'Jean Doute',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_oneline(self):
        with open('bibtexparser/tests/data/article_oneline.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': 'Jean Cesar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Baltazar2013',
                     'year': '2013',
                     'author': 'Jean Baltazar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)


    def test_article_start_with_whitespace(self):
        with open('bibtexparser/tests/data/article_start_with_whitespace.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            self.assertEqual(len(bib.get_entry_list()), 2)

    def test_article_comma_first(self):
        with open('bibtexparser/tests/data/article_comma_first.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'author': 'Jean Cesar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     },
                    {'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'ID': 'Baltazar2013',
                     'year': '2013',
                     'author': 'Jean Baltazar',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title'
                     }]
        self.assertEqual(res, expected)

    def test_article_no_braces(self):
        with open('bibtexparser/tests/data/article_no_braces.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'pages': '12-23',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'month': 'jan',
                     'author': 'Jean C{\\\'e}sar{\\\"u}',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title',
                     'abstract': "This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word",
                     },
                     ]
        self.assertEqual(res, expected)

    def test_article_special_characters(self):
        with open('bibtexparser/tests/data/article_with_special_characters.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': 'Nice Journal',
                     'volume': '12',
                     'pages': '12-23',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'month': 'jan',
                     'author': 'Jean C{\\\'e}sar{\\\"u}',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': 'An amazing title',
                     'abstract': "This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word",
                     },
                     ]
        self.assertEqual(res, expected)

    def test_article_protection_braces(self):
        with open('bibtexparser/tests/data/article_with_protection_braces.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
        expected = [{'ENTRYTYPE': 'article',
                     'journal': '{Nice Journal}',
                     'volume': '12',
                     'pages': '12-23',
                     'ID': 'Cesar2013',
                     'year': '2013',
                     'month': 'jan',
                     'author': 'Jean César',
                     'comments': 'A comment',
                     'keyword': 'keyword1, keyword2',
                     'title': '{An amazing title}',
                     'abstract': "This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word",
                     },
                     ]
        self.assertEqual(res, expected)


    ###########
    # BOOK
    ###########
    def test_book(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
            expected = [{'ENTRYTYPE': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'ID': 'Bird1987',
                         'volume': '1',
                         'title': 'Dynamics of Polymeric Liquid',
                         'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'
                         }]

        self.assertEqual(res, expected)

    def test_book_cust_unicode(self):
        with open('bibtexparser/tests/data/book_capital_AND.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=customizations_unicode)
            res = bib.get_entry_list()
            expected = [{'ENTRYTYPE': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'ID': 'Bird1987',
                         'volume': '1',
                         'title': 'Dynamics of Polymeric Liquid',
                         'author': ['Bird, R.B.', 'Armstrong, R.C.', 'Hassager, O.']
                         }]

        self.assertEqual(res, expected)

    def test_book_cust_latex(self):
        with open('bibtexparser/tests/data/book.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=customizations_latex)
            res = bib.get_entry_list()
            expected = [{'ENTRYTYPE': 'book',
                         'year': '1987',
                         'edition': '2',
                         'publisher': 'Wiley Edition',
                         'ID': 'Bird1987',
                         'volume': '1',
                         'title': '{D}ynamics of {P}olymeric {L}iquid',
                         'author': ['Bird, R.B.', 'Armstrong, R.C.', 'Hassager, O.']
                         }]

        self.assertEqual(res, expected)

    def test_traps(self):
        with codecs.open('bibtexparser/tests/data/traps.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
            expected = [{'keywords': 'keyword1, keyword2',
                         'ENTRYTYPE': 'article',
                         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                         'year': '2013',
                         'journal': 'Nice Journal',
                         'ID': 'Laide2013',
                         'pages': '12-23',
                         'title': '{An} amazing {title}',
                         'comments': 'A comment',
                         'author': 'Jean Laid{\\\'e},\nBen Loaeb',
                         'volume': 'n.s.~2',
                         'month': 'jan'
                         }]
        self.assertEqual(res, expected)

    def test_features(self):
        with open('bibtexparser/tests/data/features.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
            expected = [{'ENTRYTYPE': 'inproceedings',
                         'year': '2014',
                         'title': 'Cool Stuff',
                         'author': 'John',
                         'ID': 'mykey',
                         'booktitle': 'My International Conference',
                         }]
        self.assertEqual(res, expected)

    def test_features2(self):
        with open('bibtexparser/tests/data/features2.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
            expected = [{'ENTRYTYPE': 'inproceedings',
                         'year': '2014',
                         'title': 'Cool Stuff',
                         'author': 'John Doe',
                         'ID': 'mykey',
                         'booktitle': 'My International Conference',
                         'note': 'Email: John.Doe@example.com',
                         'pages': '1--10',
                         }]
        self.assertEqual(res, expected)

    def test_nonstandard_ignored(self):
        with open('bibtexparser/tests/data/wrong.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
            expected = [{'author': 'correct',
                         'ID': 'bar',
                         'ENTRYTYPE': 'article'}]
        self.assertEqual(res, expected)

    def test_nonstandard_not_ignored(self):
        with open('bibtexparser/tests/data/wrong.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), ignore_nonstandard_types=False)
            res = bib.get_entry_list()
        self.assertEqual(len(res), 2)

    def test_encoding(self):
        with codecs.open('bibtexparser/tests/data/encoding.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
            res = bib.get_entry_list()
            expected = [{'keywords': 'keyword1, keyword2',
                         'ENTRYTYPE': 'article',
                         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
                         'year': '2013',
                         'journal': 'Elémentaire',
                         'ID': 'Cesar_2013',
                         'pages': '12-23',
                         'title': 'An amazing title: à',
                         'comments': 'A comment',
                         'author': 'Jean César',
                         'volume': '12',
                         'month': 'jan'
                         }]
        self.assertEqual(res, expected)

    def test_encoding_with_homogenize(self):
        with codecs.open('bibtexparser/tests/data/encoding.bib', 'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read(), customization=homogenize_latex_encoding)
            res = bib.get_entry_list()
            expected = [{'keywords': 'keyword1, keyword2',
                         'ENTRYTYPE': 'article',
                         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french {\\\'e}rudit word',
                         'year': '2013',
                         'journal': 'El{\\\'e}mentaire',
                         'ID': 'Cesar_2013',
                         'pages': '12-23',
                         'title': '{A}n amazing title: {\\`a}',
                         'comments': 'A comment',
                         'author': 'Jean C{\\\'e}sar',
                         'volume': '12',
                         'month': 'jan'
                         }]
        self.assertEqual(res, expected)

    def test_field_name_with_dash_underscore(self):
        with open('bibtexparser/tests/data/article_field_name_with_underscore.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read())
        res = bib.get_entry_list()
        expected = [{
            'keyword': 'keyword1, keyword2',
            'ENTRYTYPE': 'article',
            'year': '2013',
            'journal': 'Nice Journal',
            'ID': 'Cesar2013',
            'pages': '12-23',
            'title': 'An amazing title',
            'comments': 'A comment',
            'author': 'Jean César',
            'volume': '12',
            'strange_field_name': 'val',
            'strange-field-name2': 'val2',
            }]
        self.assertEqual(res, expected)

    def test_string_definitions(self):
        with open('bibtexparser/tests/data/article_with_strings.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), common_strings=True)
        res = dict(bib.strings)
        expected = COMMON_STRINGS.copy()
        expected.update({
                'nice_journal': 'Nice Journal',
                'jean': 'Jean',
                'cesar': "César",
                })
        self.assertEqual(res, expected)

    def test_string_is_interpolated(self):
        with open('bibtexparser/tests/data/article_with_strings.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), common_strings=True,
                               interpolate_strings=True)
        res = bib.get_entry_list()
        expected = [{
            'keyword': 'keyword1, keyword2',
            'ENTRYTYPE': 'article',
            'year': '2013',
            'month': 'January',
            'journal': 'Nice Journal',
            'ID': 'Cesar2013',
            'pages': '12-23',
            'title': 'An amazing title',
            'comments': 'A comment',
            'author': 'Jean César',
            'volume': '12',
            }]
        self.assertEqual(res, expected)

    def test_string_is_not_interpolated(self):
        with open('bibtexparser/tests/data/article_with_strings.bib', 'r') as bibfile:
            bib = BibTexParser(bibfile.read(), common_strings=True,
                               interpolate_strings=False)
        res = bib.get_entry_list()[0]
        self.assertIsInstance(res['month'], BibDataStringExpression)
        self.assertEqual(len(res['month'].expr), 1)
        self.assertEqual(res['month'].get_value(), 'January')
        self.assertIsInstance(res['author'], BibDataStringExpression)
        self.assertEqual(len(res['author'].expr), 3)
        self.assertEqual(res['author'].get_value(), 'Jean César')
        self.assertIsInstance(res['journal'], BibDataStringExpression)
        self.assertEqual(len(res['journal'].expr), 1)
        self.assertEqual(res['journal'].get_value(), 'Nice Journal')

    def test_comments_spaces_and_declarations(self):
        with codecs.open(
                'bibtexparser/tests/data/comments_spaces_and_declarations.bib',
                'r', 'utf-8') as bibfile:
            bib = BibTexParser(bibfile.read())
        res_dict = bib.get_entry_dict()
        expected_dict = {'Cesar2013': {
            'keyword': 'keyword1, keyword2',
            'ENTRYTYPE': 'article',
            'abstract': 'This is an abstract. This line should be long enough to test\nmultilines... and with a french érudit word',
            'year': '2013',
            'journal': 'Nice Journal',
            'ID': 'Cesar2013',
            'pages': '12-23',
            'title': 'A great title',
            'comments': 'A comment',
            'author': 'Jean César',
            'volume': '12',
            'month': 'jan'
        }}
        self.assertEqual(res_dict, expected_dict)
        self.assertEqual(bib.preambles, ["Blah blah"])

    def test_does_not_fail_on_non_bibtex_with_partial(self):
        bibraw = '''@misc{this looks,
          like = a = bibtex file but
              , is not a real one!
        '''
        parser = BibTexParser()
        bib = parser.parse(bibraw, partial=False)
        self.assertEqual(bib.entries, [])
        self.assertEqual(bib.preambles, [])
        self.assertEqual(bib.strings, {})
        self.assertEqual(bib.comments, [
            '@misc{this looks,\n'
            '          like = a = bibtex file but\n'
            '              , is not a real one!'])

    def test_no_citekey_parsed_as_comment(self):
        bib = BibTexParser('@BOOK{, title = "bla"}')
        self.assertEqual(bib.entries, [])
        self.assertEqual(bib.preambles, [])
        self.assertEqual(bib.strings, {})
        self.assertEqual(bib.comments, ['@BOOK{, title = "bla"}'])


if __name__ == '__main__':
    unittest.main()
