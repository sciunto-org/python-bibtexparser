#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import unittest

from bibtexparser.customization import getnames


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
