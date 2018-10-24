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

    def test_entry_declaration_after_space(self):
        self.expr.entry.parseString('  @journal{key, name = {abcd}}')

    def test_entry_declaration_no_key(self):
        with self.assertRaises(self.expr.ParseException):
            self.expr.entry.parseString('@misc{name = {abcd}}')

    def test_entry_declaration_no_key_new_line(self):
        with self.assertRaises(self.expr.ParseException):
            self.expr.entry.parseString('@misc{\n name = {abcd}}')

    def test_entry_declaration_no_key_comma(self):
        with self.assertRaises(self.expr.ParseException):
            self.expr.entry.parseString('@misc{, \nname = {abcd}}')

    def test_entry_declaration_no_key_keyvalue_without_space(self):
        with self.assertRaises(self.expr.ParseException):
            self.expr.entry.parseString('@misc{\nname=aaa}')

    def test_entry_declaration_key_with_whitespace(self):
        with self.assertRaises(self.expr.ParseException):
            self.expr.entry.parseString('@misc{ xx yy, \n name = aaa}')

    def test_string_declaration_after_space(self):
        self.expr.string_def.parseString('  @string{ name = {abcd}}')

    def test_preamble_declaration_after_space(self):
        self.expr.preamble_decl.parseString('  @preamble{ "blah blah " }')

    def test_declaration_after_space(self):
        keys = []
        self.expr.entry.addParseAction(
            lambda s, l, t: keys.append(t.get('Key'))
        )
        self.expr.main_expression.parseString(' @journal{key, name = {abcd}}')
        self.assertEqual(keys, ['key'])

    def test_declaration_after_space_and_comment(self):
        keys = []
        self.expr.entry.addParseAction(
            lambda s, l, t: keys.append(t.get('Key'))
        )
        self.expr.main_expression.parseString(
            '% Implicit comment\n @article{key, name={abcd}}'
        )
        self.assertEqual(keys, ['key'])
