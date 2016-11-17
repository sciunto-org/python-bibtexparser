#!/usr/bin/env python

"""
test for author list parsing code -- really complex!

These tests have every example that is in The LaTeX companion, so it's at least close!
"""

# imports to make code as py2-py3 compatible as possible
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# I really like pytest -- unittest is painful!

import pytest

from bibtexparser.author_parse import (Author,
                                       parse_author,
                                       split_authors,
                                       firstislower,
                                       pre_process_brackets,
                                       post_process_brackets,
                                       )

from bibtexparser.customization import splitname

## little wrapper so I can test the splitname() function with the same tests.

def parse_author(name_string):
    result = splitname(name_string)

    result = {key: " ".join(part) for key, part in result.items()}

    return Author(result['first'], result['von'], result['last'], result['jr'])


# fixme: This could be made much cleaner with parameterized tests!

class Test_parse_name():

    def test_simplest(self):
        name = "Christopher Barker"
        author = parse_author(name)
        assert author.first == "Christopher"
        assert author.last == "Barker"
        assert author.von == ""
        assert author.jr == ""

    def test_last_only(self):
        name = "Barker"
        author = parse_author(name)
        assert author.first == ""
        assert author.last == "Barker"
        assert author.von == ""
        assert author.jr == ""

    def test_simple(self):
        """the no comma version"""
        name = "Donald E. Knuth"
        author = parse_author(name)
        assert author.first == "Donald E."
        assert author.last == "Knuth"
        assert author.von == ""
        assert author.jr == ""

    def test_simple2(self):
        """other ways of handling first name"""
        name = "D. E. Knuth"
        author = parse_author(name)
        assert author.first == "D. E."
        assert author.last == "Knuth"
        assert author.von == ""
        assert author.jr == ""

    def test_simple2(self):
        """other ways of handling first name"""
        name = "D[onald] E. Knuth"
        author = parse_author(name)
        assert author.first == "D[onald] E."
        assert author.last == "Knuth"
        assert author.von == ""
        assert author.jr == ""

    # Apparently, there are three possible forms:
    #  "First von Last" "von Last, First" "von Last, Jr, First"
    def test_option1(self):
        """the no comma version"""
        name = "First von Last"
        author = parse_author(name)
        assert author.first == "First"
        assert author.last == "Last"
        assert author.von == "von"
        assert author.jr == ""

    def test_option2(self):
        """the no comma version"""
        name = "von Last, First"
        author = parse_author(name)
        assert author.first == "First"
        assert author.last == "Last"
        assert author.von == "von"
        assert author.jr == ""

    def test_option3(self):
        """the no comma version"""
        name = "von Last, Jr, First"
        author = parse_author(name)
        assert author.first == "First"
        assert author.last == "Last"
        assert author.von == "von"
        assert author.jr == "Jr"

    def test_all_parts(self):
        name = "von der Schmidt, Jr., Alex"
        author = parse_author(name)
        assert author.first == "Alex"
        assert author.last == "Schmidt"
        assert author.von == "von der"
        assert author.jr == "Jr."

    def test_fancy_von(self):
        """the no comma version"""
        name = "de la Porte, Files, Emile"
        author = parse_author(name)
        assert author.first == "Emile"
        assert author.last == "Porte"
        assert author.von == "de la"
        assert author.jr == "Files"

    def test_double_last(self):
        name = "Lopez Fernandez, Miguel"
        author = parse_author(name)
        assert author.first == "Miguel"
        assert author.last == "Lopez Fernandez"
        assert author.von == ""
        assert author.jr == ""

    def test_long_complex(self):
        """ example from The LaTeX companion """
        name = "Johannes Martinus Albertus van de Groene Heide"
        author = parse_author(name)
        assert author.first == "Johannes Martinus Albertus"
        assert author.last == "Groene Heide"
        assert author.von == "van de"
        assert author.jr == ""

    def test_hyphenated(self):
        """ example from The LaTeX companion """
        name = "Maria-Victoria Delgrande"
        author = parse_author(name)
        assert author.first == "Maria-Victoria"
        assert author.last == "Delgrande"
        assert author.von == ""
        assert author.jr == ""

    def test_von_and_first_last(self):
        """ example from The LaTeX companion """
        name = "von der Schmidt, Alex"
        author = parse_author(name)
        assert author.first == "Alex"
        assert author.last == "Schmidt"
        assert author.von == "von der"
        assert author.jr == ""

    def test_comma_junior(self):
        """ example from The LaTeX companion """
        name = "Smith, Jr., Robert"
        author = parse_author(name)
        assert author.first == "Robert"
        assert author.last == "Smith"
        assert author.von == ""
        assert author.jr == "Jr."

    def test_von_in_brackets(self):
        """ example from The LaTeX companion """
        name = "{von der Schmidt}, Alex"
        author = parse_author(name)
        assert author.first == "Alex"
        assert author.last == "{von der Schmidt}"
        assert author.von == ""
        assert author.jr == ""

    def test_jr_in_brackets(self):
        """ example from The LaTeX companion """
        name = "{Lincoln Jr.}, John P."
        author = parse_author(name)
        assert author.first == "John P."
        assert author.last == "{Lincoln Jr.}"
        assert author.von == ""
        assert author.jr == ""

    def test_jr_in_brackets_end(self):
        """ example from The LaTeX companion """
        name = "John P. {Lincoln Jr.}"
        author = parse_author(name)
        assert author.first == "John P."
        assert author.last == "{Lincoln Jr.}"
        assert author.von == ""
        assert author.jr == ""


#    @pytest.mark.xfail
    def test_uppercase_von(self):
        """ example from The LaTeX companion
            This is how it is suggested to have an uppercase von
        """
        name = r"Maria {\uppercase{d}e La} Cruz"
        author = parse_author(name)
        print(author)
        assert author.first == "Maria"
        assert author.last == "Cruz"
        assert author.von == r"{\uppercase{d}e La}"
        assert author.jr == ""


class Test_brackets():
    """
    test the bracket handling
    """
    # fixme: these are hard-coding the replacement strings -- they chould get the constants
    #        from the module

    def test_replace_space(self):
        string = "{von der Schmidt}, Alex)"
        result = pre_process_brackets(string)

        assert result == "{von\uE000der\uE000Schmidt}, Alex)"

    def test_replace_comma(self):
        string = "{This,that}, Alex)"
        result = pre_process_brackets(string)

        assert result == "{This\uE001that}, Alex)"

    def test_replace_both(self):
        string = "{Boss and Friends, Inc.} and {Snoozy and Boys, Ltd.}"
        result = pre_process_brackets(string)

        assert result == "{Boss\uE000and\uE000Friends\uE001\uE000Inc.} and {Snoozy\uE000and\uE000Boys\uE001\uE000Ltd.}"

    def test_replace_nested(self):
        string = "{Boss and Friends, Inc.} and {{Snoozy, Jr} and Boys, Ltd.}"
        result = pre_process_brackets(string)

        assert result == "{Boss\uE000and\uE000Friends\uE001\uE000Inc.} and {{Snoozy\uE001\uE000Jr}\uE000and\uE000Boys\uE001\uE000Ltd.}"

    def test_reverse_both(self):
        string = "{Boss\uE000and\uE000Friends\uE001\uE000Inc.} and {{Snoozy\uE001\uE000Jr}\uE000and\uE000Boys\uE001\uE000Ltd.}"
        result = post_process_brackets(string)
        assert result == "{Boss and Friends, Inc.} and {{Snoozy, Jr} and Boys, Ltd.}"

    def test_round_trip_both(self):
        string = "{Boss and Friends, Inc.} and {{Snoozy, Jr} and Boys, Ltd.}"
        result = pre_process_brackets(string)
        result = post_process_brackets(result)
        assert result == string

    def test_firstislower(self):
        assert firstislower(r"{\uppercase{d}e La}")


class Test_author_split():

    def test_one_author(self):
        authors = split_authors("Johannes Martinus Albertus van de Groene Heide")
        assert authors == ["Johannes Martinus Albertus van de Groene Heide"]

    def test_simple(self):
        authors = split_authors("Frank Mittlebach and Rowley, Chris")
        assert authors == ["Frank Mittlebach", "Rowley, Chris"]

    def test_and_in_brackets(self):
        authors = split_authors("{Lion and Nobel, Ltd}")
        print("in test:", authors)
        assert authors == ["{Lion and Nobel, Ltd}"]

    def test_and_in_and_out_brackets(self):
        authors = split_authors("{Boss and Friends, Inc.} and {{Snoozy, Jr} and Boys, Ltd.}")
        assert authors == ["{Boss and Friends, Inc.}", "{{Snoozy, Jr} and Boys, Ltd.}"]
