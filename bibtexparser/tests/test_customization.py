#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest

from bibtexparser.customization import getnames, convert_to_unicode, homogeneize_latex_encoding, page_double_hyphen, keyword


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

    ###########
    # homogeneize
    ###########
    def test_homogeneize(self):
        record = {'toto': 'à {\`a} \`{a}'}
        result = homogeneize_latex_encoding(record)
        expected = {'toto': '{\`a} {\`a} {\`a}'}
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
