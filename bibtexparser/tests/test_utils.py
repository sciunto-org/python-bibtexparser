#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from bibtexparser.utils import splitnames


class TestUtilsMethods(unittest.TestCase):

    ###########
    # splitnames
    ###########
    def test_splitnames(self):
        """Test utils.splitnames()"""
        tests = (
            ("Simple Name", ["Simple Name"]),
            ("First Name and Last Name", ["First Name", "Last Name"]),
            ("First Name AND Last Name", ["First Name", "Last Name"]),
            ("First Name And Last Name", ["First Name", "Last Name"]),
            ("First Name aNd Last Name", ["First Name", "Last Name"]),
            ("First Name    and Last Name", ["First Name", "Last Name"]),
            ("First Name and   Last Name", ["First Name", "Last Name"]),
            ("First Name    and    Last Name", ["First Name", "Last Name"]),
            ("{Simon and Schuster}", ["{Simon and Schuster}"]),
            ("Something \\and Other", ["Something \\and Other"]),
            ("Name One and Two, Name and Name Three", ["Name One", "Two, Name", "Name Three"]),
            ("P. M. Sutherland and Smith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland and\tSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland and\nSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland AND\tSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland AND\nSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland And\tSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland And\nSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland aNd\tSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("P. M. Sutherland aNd\nSmith, J.", ["P. M. Sutherland", "Smith, J."]),
            ("Fake Name an{d brace in an}d and Somebody Else", ["Fake Name an{d brace in an}d", "Somebody Else"]),
            ("and John Smith", ["and John Smith"]),
            (" and John Smith", ["and John Smith"]),
            ("and John Smith and Phil Holden", ["and John Smith", "Phil Holden"]),
            (" and John Smith and Phil Holden", ["and John Smith", "Phil Holden"]),
            ("\tand John Smith and Phil Holden", ["and John Smith", "Phil Holden"]),
            ("\nand John Smith and Phil Holden", ["and John Smith", "Phil Holden"]),
            ("John Smith and Phil Holden and", ["John Smith", "Phil Holden and"]),
            ("John Smith and Phil Holden and ", ["John Smith", "Phil Holden and"]),
            ("John Smith and Phil Holden and\n", ["John Smith", "Phil Holden and"]),
            ("John Smith and Phil Holden and\t", ["John Smith", "Phil Holden and"]),
            ("Harry Fellowes and D. Drumpf", ["Harry Fellowes", "D. Drumpf"]),
            ("Harry Fellowes~and D. Drumpf", ["Harry Fellowes~and D. Drumpf"]),
            ("Harry Fellowes~and~D. Drumpf", ["Harry Fellowes~and~D. Drumpf"]),
            ("Harry Fellowes and~D. Drumpf", ["Harry Fellowes and~D. Drumpf"]),
            ("      ", []),
            ("\t\n \t", []),
            ("~", ["~"]),
            ("~~~ and J. Smith", ["~~~", "J. Smith"]),
        )
        for names, expected in tests:
            self.assertEqual(splitnames(names), expected)


