#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from bibtexparser.customization import getnames, convert_to_unicode


class TestBibtexParserMethod(unittest.TestCase):

    def test_getnames(self):
        names = ['Foo Bar',
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
                    'Bar, F',
                    'de Savigny, Jean',
                    'la Tour, Jean',
                    'le Tour, Jean',
                    'ben Akar, Mike',
                    #'de la Tour, Jean',
                    #'van der Waals, Johannes Diderik',
                    ]
        self.assertEqual(result, expected)

    def test_convert_to_unicode(self):
        record = {'toto': '{\`a} \`{a}'}
        result = convert_to_unicode(record)
        expected = {'toto': 'à à'}
        self.assertEqual(result, expected)
