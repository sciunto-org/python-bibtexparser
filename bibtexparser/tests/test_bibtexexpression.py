#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
import unittest

from bibtexparser.bibtexexpression import BibtexExpression


class TestBibtexExpression(unittest.TestCase):

    def setUp(self):
        self.expr = BibtexExpression()

    def test_minimal(self):
        result = self.expr.entry.parseString('@journal{key, name = 123 }')
        self.assertEqual(result.get('EntryType'), 'journal')
        self.assertEqual(result.get('Key'), 'key')
        self.assertEqual(result.get('Fields'), {'name': '123'})

    def test_capital_type(self):
        result = self.expr.entry.parseString('@JOURNAL{key, name = 123 }')
        self.assertEqual(result.get('EntryType'), 'JOURNAL')

    def test_capital_key(self):
        result = self.expr.entry.parseString('@journal{KEY, name = 123 }')
        self.assertEqual(result.get('Key'), 'KEY')

    def test_braced(self):
        result = self.expr.entry.parseString('@journal{key, name = {abc} }')
        self.assertEqual(result.get('Fields'), {'name': 'abc'})

    def test_braced_with_new_line(self):
        result = self.expr.entry.parseString(
            '@journal{key, name = {abc\ndef} }')
        self.assertEqual(result.get('Fields'), {'name': 'abc\ndef'})

    def test_braced_unicode(self):
        result = self.expr.entry.parseString(
            '@journal{key, name = {àbcđéf} }')
        self.assertEqual(result.get('Fields'), {'name': 'àbcđéf'})

    def test_quoted(self):
        result = self.expr.entry.parseString('@journal{key, name = "abc" }')
        self.assertEqual(result.get('Fields'), {'name': 'abc'})

    def test_quoted_with_new_line(self):
        result = self.expr.entry.parseString(
            '@journal{key, name = "abc\ndef" }')
        self.assertEqual(result.get('Fields'), {'name': 'abc\ndef'})

    def test_quoted_with_unicode(self):
        result = self.expr.entry.parseString(
            '@journal{key, name = "àbcđéf" }')
        self.assertEqual(result.get('Fields'), {'name': 'àbcđéf'})
