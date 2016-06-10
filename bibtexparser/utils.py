#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
General utility functions for working with BibTeX data.
"""


def splitnames(names):
    """
    Splits a string of multiple names.

    :param string names: a string containing one or more names
    :returns: list of strings, one entry per name in the input

    In BibTeX a set of names (e.g., authors or editors) are separated by the
    word 'and'. Any instances of the word 'and' within a pair of braces is
    treated as part of the name, and not a separator.

    This function takes a string containing one or more names, and splits them
    into a list of individual names. They are returned as a list of strings. If
    the input contains only whitespace characters, an empty list is returned.

    Note that for consistency with the way BibTeX splits strings, the
    non-breaking space or tie '~' is treated as a regular character and not
    whitespace.

    No error checking is performed on the individual names, i.e., there is no
    guarantee that the entries in the returned list are valid BibTeX names.

    Examples::

        >>> from bibtexparser.utils import splitnames

        >>> splitnames('Donald E. Knuth')
        ['Donald E. Knuth']

        >>> splitnames('Donald E. Knuth and Leslie Lamport')
        ['Donald E. Knuth', 'Leslie Lamport']

        >>> splitnames('{Simon and Schuster}')
        ['{Simon and Schuster}']

    """
    # Sanity check for empty string.
    names = names.strip(' \r\n\t')
    if not names:
        return []

    # Steps to find the ' and ' token.
    START_WHITESPACE, FIND_A, FIND_N, FIND_D, END_WHITESPACE, NEXT_WORD = 0, 1, 2, 3, 4, 5

    # Processing variables.
    step = START_WHITESPACE         # Current step.
    pos = 0                         # Current position in string.
    bracelevel = 0                  # Current bracelevel.
    spans = [[0]]                   # Spans of names within the string.
    possible_end = 0                # Possible end position of a name.
    whitespace = set(' \r\n\t')     # Allowed whitespace characters.

    # Loop over the string.
    namesiter = iter(names)
    for char in namesiter:
        pos += 1

        # Escaped character.
        if char == '\\':
            next(namesiter)
            pos += 1
            continue

        # Change in brace level.
        if char == '{':
            bracelevel += 1
            step = START_WHITESPACE
            continue
        if char == '}':
            if bracelevel:
                bracelevel -= 1
            step = START_WHITESPACE
            continue

        # Ignore everything inside a brace.
        if bracelevel:
            step = START_WHITESPACE
            continue

        # Looking for a whitespace character to start the ' and '. When we find
        # one, mark it as the possible end of the previous word.
        if step == START_WHITESPACE:
            if char in whitespace:
                step = FIND_A
                possible_end = pos - 1

        # Looking for the letter a. NB., we can have multiple whitespace
        # characters so we need to handle that here.
        elif step == FIND_A:
            if char in ('a', 'A'):
                step = FIND_N
            elif char not in whitespace:
                step = START_WHITESPACE

        # Looking for the letter n.
        elif step == FIND_N:
            if char in ('n', 'N'):
                step = FIND_D
            else:
                step = START_WHITESPACE

        # Looking for the letter d.
        elif step == FIND_D:
            if char in ('d', 'D'):
                step = END_WHITESPACE
            else:
                step = START_WHITESPACE

        # And now the whitespace to end the ' and '.
        elif step == END_WHITESPACE:
            if char in whitespace:
                step = NEXT_WORD
            else:
                step = START_WHITESPACE

        # Again, we need to handle multiple whitespace characters. Keep going
        # until we find the start of the next word.
        elif step == NEXT_WORD:
            if char not in whitespace:
                # Finish the previous word span, start the next,
                # and do it all again.
                spans[-1].append(possible_end)
                spans.append([pos-1])
                step = START_WHITESPACE

    # Finish the last word.
    spans[-1].append(None)

    # Extract and return the names.
    return [names[start:end] for start, end in spans]
