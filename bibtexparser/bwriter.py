#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import logging
from .bibdatabase import BibDatabase

logger = logging.getLogger(__name__)

__all__ = ['BibTexWriter']


def to_bibtex(parsed):
    """
    Convenience function for backwards compatibility.
    """
    return BibTexWriter().write(parsed)


class BibTexWriter(object):
    """
    Writer to convert a :class:`BibDatabase` object to a string or file formatted as a BibTeX file.

    Example::

        from bibtexparser.bwriter import BibTexWriter

        bib_database = ...

        writer = BibTexWriter()
        writer.contents = ['comments', 'entries']
        writer.indent = '  '
        writer.order_entries_by = ('ENTRYTYPE', 'author', 'year')
        bibtex_str = bibtexparser.dumps(bib_database, writer)

    """

    _valid_contents = ['entries', 'comments', 'preambles', 'strings']

    def __init__(self):
        #: List of BibTeX elements to write, valid values are `entries`, `comments`, `preambles`, `strings`.
        self.contents = ['comments', 'preambles', 'strings', 'entries']
        #: Character(s) for indenting BibTeX field-value pairs. Default: single space.
        self.indent = ' '
        #: Characters(s) for separating BibTeX entries. Default: new line.
        self.entry_separator = '\n'
        #: Tuple of fields for ordering entries. Set to `None` to disable sorting. Default: BibTeX key `('ID', )`.
        self.order_entries_by = ('ID', )
        #: BibTeX syntax allows comma first syntax
        #: (common in functional languages), use this to enable
        #: comma first syntax as the bwritter output
        self.comma_first = False

    def write(self, bib_database):
        """
        Converts a bibliographic database to a BibTeX-formatted string.

        :param bib_database: bibliographic database to be converted to a BibTeX string
        :type bib_database: BibDatabase
        :return: BibTeX-formatted string
        :rtype: str or unicode
        """
        bibtex = ''
        for content in self.contents:
            try:
                # Add each element set (entries, comments)
                bibtex += getattr(self, '_' + content + '_to_bibtex')(bib_database)
            except AttributeError:
                logger.warning("BibTeX item '{}' does not exist and will not be written. Valid items are {}."
                               .format(content, self._valid_contents))
        return bibtex

    def _entries_to_bibtex(self, bib_database):
        bibtex = ''
        if self.order_entries_by:
            # TODO: allow sort field does not exist for entry
            entries = sorted(bib_database.entries, key=lambda x: BibDatabase.entry_sort_key(x, self.order_entries_by))
        else:
            entries = bib_database.entries

        for entry in entries:
            bibtex += self._entry_to_bibtex(entry)
        return bibtex

    def _entry_to_bibtex(self, entry):
        bibtex = ''
        # Write BibTeX key
        bibtex += '@' + entry['ENTRYTYPE'] + '{' + entry['ID']

        # Write field = value lines
        for field in [i for i in sorted(entry) if i not in ['ENTRYTYPE', 'ID']]:
            try:
                if self.comma_first:
                    bibtex += "\n," + self.indent + field + " = {" + entry[field] + "}"
                else:
                    bibtex += ",\n" + self.indent + field + " = {" + entry[field] + "}"
            except TypeError:
                raise TypeError("The field %s in entry %s must be a string"
                                % (field, entry['ID']))
        bibtex += "\n}\n" + self.entry_separator
        return bibtex

    def _comments_to_bibtex(self, bib_database):
        return ''.join(['@comment{{{0}}}\n{1}'.format(comment, self.entry_separator)
                        for comment in bib_database.comments])

    def _preambles_to_bibtex(self, bib_database):
        return ''.join(['@preamble{{{0}}}\n{1}'.format(preamble, self.entry_separator)
                        for preamble in bib_database.preambles])

    def _strings_to_bibtex(self, bib_database):
        return ''.join(['@string{{{0} = "{1}"}}\n{2}'.format(name, value, self.entry_separator)
                        for name, value in bib_database.strings.items()])
