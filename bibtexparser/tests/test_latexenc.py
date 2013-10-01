#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# Author: Francois Boulogne <fboulogne at sciunto dot org>, 2012

import unittest

from bibtexparser.latexenc import *

class TestLatexConverter(unittest.TestCase):

    def test_accent(self):
        string = 'à é è ö'
        result = string_to_latex(string)
        expected = "\`{a} \\\'{e} \`{e} \\\"{o}"
        self.assertEqual(result, expected)

    def test_accent(self):
        """ Don't touch { and }"""
        string = '{A}'
        result = string_to_latex(string)
        expected = '{A}'
        self.assertEqual(result, expected)

class TestUppercaseProtection(unittest.TestCase):

    def test_uppercase(self):
        string = 'A'
        result = protect_uppercase(string)
        expected = '{A}'
        self.assertEqual(result, expected)

    def test_lowercase(self):
        string = 'a'
        result = protect_uppercase(string)
        expected = 'a'
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
