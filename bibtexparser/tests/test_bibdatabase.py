import unittest
from bibtexparser.bibdatabase import (BibDatabase, BibDataString,
                                      BibDataStringExpression)


class TestBibDatabase(unittest.TestCase):
    entries = [{'ENTRYTYPE': 'book',
                'year': '1987',
                'edition': '2',
                'publisher': 'Wiley Edition',
                'ID': 'Bird1987',
                'volume': '1',
                'title': 'Dynamics of Polymeric Liquid',
                'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'
                }]

    def test_entries_list_method(self):
        bib_db = BibDatabase()
        bib_db.entries = self.entries
        self.assertEqual(bib_db.entries, bib_db.get_entry_list())

    def test_entries_dict_prop(self):
        bib_db = BibDatabase()
        bib_db.entries = self.entries
        self.assertEqual(bib_db.entries_dict, bib_db.get_entry_dict())


class TestBibDataString(unittest.TestCase):

    def setUp(self):
        self.bd = BibDatabase()

    def test_name_is_lower(self):
        bds = BibDataString(self.bd, 'nAmE')
        self.assertTrue(bds.name.islower())

    def test_raises_KeyError(self):
        bds = BibDataString(self.bd, 'name')
        with self.assertRaises(KeyError):
            bds.get_value()

    def test_get_value(self):
        bds = BibDataString(self.bd, 'name')
        self.bd.strings['name'] = 'value'
        self.assertEqual(bds.get_value(), 'value')

    def test_expand_string(self):
        bds = BibDataString(self.bd, 'name')
        self.bd.strings['name'] = 'value'
        self.assertEqual(BibDataString.expand_string('name'), 'name')
        self.assertEqual(BibDataString.expand_string(bds), 'value')

    def test_get_value_string_is_defined_by_expression(self):
        self.bd.strings['name'] = 'string'
        exp = BibDataStringExpression(['this is a ',
                                       BibDataString(self.bd, 'name')])
        self.bd.strings['exp'] = exp
        bds = BibDataString(self.bd, 'exp')
        self.assertEqual(bds.get_value(), 'this is a string')

    def test_strings_are_equal_iif_name_is_equal(self):
        self.bd.strings['a'] = 'foo'
        self.bd.strings['b'] = 'foo'
        a1 = BibDataString(self.bd, 'a')
        a2 = BibDataString(self.bd, 'a')
        b = BibDataString(self.bd, 'b')
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)
        self.assertNotEqual(a1, b)
        self.assertNotEqual(a1, "foo")


class TestBibDataStringExpression(unittest.TestCase):

    def setUp(self):
        self.bd = BibDatabase()
        self.bd.strings['name'] = 'value'
        self.bds = BibDataString(self.bd, 'name')

    def test_get_value(self):
        exp = BibDataStringExpression(
            ["The string has value: ", self.bds, '.'])
        self.assertEqual(exp.get_value(), 'The string has value: value.')

    def test_raises_KeyError(self):
        bds = BibDataString(self.bd, 'unknown')
        exp = BibDataStringExpression([bds, self.bds, 'text'])
        with self.assertRaises(KeyError):
            exp.get_value()

    def test_equations_are_equal_iif_same(self):
        a1 = BibDataString(self.bd, 'a')
        a2 = BibDataString(self.bd, 'a')
        exp = BibDataStringExpression([a1, self.bds, 'text'])
        self.assertEqual(exp, BibDataStringExpression([a2, self.bds, 'text']))
        self.assertNotEqual(exp, BibDataStringExpression(['foo', self.bds, 'text']))
        self.assertNotEqual(exp, 'foovaluetext')


if __name__ == '__main__':
    unittest.main()
