#!/usr/bin/env python


"""
This module allows parsing of author string in BiBTeX files.

It does its best to follow the BiBTeX model for author names,
using info from:

http://nwalsh.com/tex/texhelp/bibtx-23.html

and

"The LaTeX companion"

The tests include all the examples in The LaTeX Companion (1993)

NOTE: This would probably be more robust if it were re-written to do the tokenizing
      directly in a TeX aware way i.e. handling {} and \commands{} exactly like TeX does.
      But then it couldn't use python's nifty built-in string methods for splitting, etc.
"""

# imports to make code as py2-py3 compatible as possible
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

# some global constants:

# These are used to prevent str.split() from spilling on things inside brackets
# The use Unicode "Private use areas", so they wo'nt confilict with real text
REPLACE_SPACE = "\uE000"
REPLACE_COMMA = "\uE001"

# using a namedtuple for the author -- so yu can get the parts, or simple use as a tuple

Author = namedtuple('Author', ['first', 'von', 'last', 'jr'])


def split_authors(author_str):
    """
    parses a complete author string to break up into multiple authors
    returns a list of authors: each author is a string
    """
    print(author_str)

    # splitting on "and", but bracket aware:
    brackets = 0
    and_ind = []
    for i, c in enumerate(author_str[:]):
        if c == "{":
            brackets += 1
        elif c == "}":
            brackets -= 1
        elif not brackets:
            if author_str[i:i + 3] == "and":
                and_ind.append(i)
    print("and indexes:", and_ind)
    authors = []
    for i in and_ind:
        print (author_str)
        authors.append(author_str[:i].strip())
        author_str = author_str[i + 3:]
        print(authors, author_str)
    authors.append(author_str.strip())
    print(authors)

    return authors


def firstislower(s):
    """
    an islower() function that finds if th first letter is lower case,
    ignoring TeX control sequences

    used to find "von" parts of names
    """
    ind = 0
    in_control = False
    for c in s:
        if c == "{":
            ind += 1
            in_control = False
        elif c == "\\":
            ind += 1
            in_control = True
        else:
            if not in_control:
                return c.islower()
    return False


def parse_author(string):

    r"""
    parse a BiBTeX author string

    This function finds the First, Von, Last, and Jr. parts of the author string
    as defnined by teh BiBTeX spec.

    :param string: the full author string (only one author)

    :returns: named tuple of author parts: (first, von, last, jr) with fields:
              author.first
              author.von
              author.last
              author.jr
              any piece that doesn't exist is an empty string

    at least a last name is required.

    Example:

    >>> parse_author("von der Schmidt, Jr., Alex")
    Author(first='Alex', von='von der', last='Schmidt', jr='Jr.')
    >>>

    Many more examples are in the tests.
    """

    string = pre_process_brackets(string)

    first, von, last, jr = ('',) * 4
    string = string.strip()
    # if there is a comma, the first name is after the comma
    if "," in string:
        parts = string.rsplit(",", 1)
        first = parts[1].strip()
        string = parts[0].strip()

        # now if there is still a comma, it's a Jr
        print("first name removed:", first, repr(string))
        parts = string.partition(",")
        jr = parts[2].strip()
        string = parts[0]
        print("Jr removed:", jr, repr(string))

    # now look for the von:
    #  which can be before a double last name -- arrgg!
    if string:
        print("splitting on the von")
        parts = string.split()
        print(parts)
        # look for the von parts:
        if len(parts) == 1:  # only one token, must be the last name
            last = parts[0]
        else:
            von1, von2 = -1, 0
            for i, part in enumerate(parts):
                if firstislower(part):  # It's a von
                    print("found a von:", part, von1, von2)
                    von2 = i + 1
                    von1 = i if von1 == -1 else von1
                    print(von1, von2)
            print("von indexes:", von1, von2)
            if von1 > -1:
                von = " ".join(parts[von1:von2])
                if not first:
                    first = " ".join(parts[:von1])
                last = " ".join(parts[von2:])
            else:
                if first:
                    last = " ".join(parts)
                else:
                    last = parts[-1]
                    first = " ".join(parts[:-1])

    print("last name:", last)

    return Author(*[post_process_brackets(s) for s in (first, von, last, jr)])


def pre_process_brackets(in_str, replace_and=False):
    """
    Replace whitespace and commas that are in brackets

    So that they won't be used for splitting, etc.

    fixme: It would probably be cleaner to write custom tokenizing code that
           respects brackets, rather than this kludge - but this was easy
    """
    # make sure any whitespace is a single regular space charactor:
    in_str = " ".join(in_str.split())
    out = []
    brackets = 0
    for c in in_str:
        if c == "{":
            brackets += 1
        elif c == "}":
            brackets -= 1
        if brackets:
            if c == " ":
                out.append(REPLACE_SPACE)
            elif c == ",":
                out.append(REPLACE_COMMA)
            else:
                out.append(c)
        else:
            out.append(c)
    return "".join(out)


def post_process_brackets(in_str):
    """
    return the spaces and commas inside the brackets
    """
    return in_str.replace(REPLACE_SPACE, " ").replace(REPLACE_COMMA, ",")


if __name__ == "__main__":

    main()
