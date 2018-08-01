#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest

from bibtexparser.customization import getnames, convert_to_unicode, homogenize_latex_encoding, page_double_hyphen, keyword, add_plaintext_fields


class TestBibtexParserMethod(unittest.TestCase):

    ###########
    # getnames
    ###########
    def test_getnames(self):
        names = ['Foo Bar',
                 'Foo B. Bar',
                 'F. B. Bar',
                 'F.B. Bar',
                 'F. Bar',
                 'Jean de Savigny',
                 'Jean la Tour',
                 'Jean le Tour',
                 'Mike ben Akar',
                 #'Jean de la Tour',
                 #'Johannes Diderik van der Waals',
                 ]
        result = getnames(names)
        expected = ['Bar, Foo',
                    'Bar, Foo B.',
                    'Bar, F. B.',
                    'Bar, F. B.',
                    'Bar, F.',
                    'de Savigny, Jean',
                    'la Tour, Jean',
                    'le Tour, Jean',
                    'ben Akar, Mike',
                    #'de la Tour, Jean',
                    #'van der Waals, Johannes Diderik',
                    ]
        self.assertEqual(result, expected)

    @unittest.skip('Bug #9')
    def test_getnames_braces(self):
        names = ['A. {Delgado de Molina}', 'M. Vign{\\\'e}']
        result = getnames(names)
        expected = ['Delgado de Molina, A.', 'Vigné, M.']
        self.assertEqual(result, expected)

    ###########
    # page_double_hyphen
    ###########
    def test_page_double_hyphen_alreadyOK(self):
        record = {'pages': '12--24'}
        result = page_double_hyphen(record)
        expected = record
        self.assertEqual(result, expected)

    def test_page_double_hyphen_simple(self):
        record = {'pages': '12-24'}
        result = page_double_hyphen(record)
        expected = {'pages': '12--24'}
        self.assertEqual(result, expected)

    def test_page_double_hyphen_space(self):
        record = {'pages': '12 - 24'}
        result = page_double_hyphen(record)
        expected = {'pages': '12--24'}
        self.assertEqual(result, expected)

    def test_page_double_hyphen_nothing(self):
        record = {'pages': '12 24'}
        result = page_double_hyphen(record)
        expected = {'pages': '12 24'}
        self.assertEqual(result, expected)

    ###########
    # convert to unicode
    ###########
    def test_convert_to_unicode(self):
        record = {'toto': '{\`a} \`{a}'}
        result = convert_to_unicode(record)
        expected = {'toto': 'à à'}
        self.assertEqual(result, expected)
        record = {'toto': '{\\"u} \\"{u}'}
        result = convert_to_unicode(record)
        expected = {'toto': 'ü ü'}
        self.assertEqual(result, expected)
        # From issue 121
        record = {'title': '{Two Gedenk\\"uberlieferung der Angelsachsen}'}
        result = convert_to_unicode(record)
        expected = {'title': 'Two Gedenküberlieferung der Angelsachsen'}
        self.assertEqual(result, expected)
        # From issue 161
        record = {'title': r"p\^{a}t\'{e}"}
        result = convert_to_unicode(record)
        expected = {'title': "pâté"}
        self.assertEqual(result, expected)
        record = {'title': r"\^{i}le"}
        result = convert_to_unicode(record)
        expected = {'title': "île"}
        self.assertEqual(result, expected)
        record = {'title': r"\texttimes{}{\texttimes}\texttimes"}
        result = convert_to_unicode(record)
        expected = {'title': "×××"}
        self.assertEqual(result, expected)

    ###########
    # homogenize
    ###########
    def test_homogenize(self):
        record = {'toto': 'à {\`a} \`{a}'}
        result = homogenize_latex_encoding(record)
        expected = {'toto': '{\`a} {\`a} {\`a}'}
        self.assertEqual(result, expected)

    ###########
    # add_plaintext_fields
    ###########
    def test_add_plaintext_fields(self):
        record = {
            'title': 'On-line {Recognition} of {Handwritten} {Mathematical} {Symbols}',
            'foobar': ['{FFT} {Foobar}', '{foobar}'],
            'foobar2': {'item1': '{FFT} {Foobar}', 'item2': '{foobar}'}
        }
        result = add_plaintext_fields(record)
        expected = {
            'title': 'On-line {Recognition} of {Handwritten} {Mathematical} {Symbols}',
            'plain_title': 'On-line Recognition of Handwritten Mathematical Symbols',
            'foobar': ['{FFT} {Foobar}', '{foobar}'],
            'plain_foobar': ['FFT Foobar', 'foobar'],
            'foobar2': {'item1': '{FFT} {Foobar}', 'item2': '{foobar}'},
            'plain_foobar2': {'item1': 'FFT Foobar', 'item2': 'foobar'}
        }
        self.assertEqual(result, expected)

    ###########
    # keywords
    ###########
    def test_keywords(self):
        record = {'keyword': "a b, a b , a b;a b ; a b, a b\n"}
        result = keyword(record)
        expected = {'keyword': ['a b'] * 6}
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
