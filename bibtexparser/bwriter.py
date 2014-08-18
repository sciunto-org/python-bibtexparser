#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Francois Boulogne
# License:

import logging

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
        bibtex_str = bibtexparser.dumps(bib_database, writer)

    """

    _valid_contents = ['entries', 'comments', 'preambles', 'strings']

    def __init__(self):
        #: List of BibTeX elements to write, valid values are `entries`, `comments`, `preambles`, `strings`.
        self.contents = ['entries', 'comments']
        #: Character(s) for indenting BibTeX field-value pairs. Default: single space.
        self.indent = ' '
        #: Characters(s) for separating BibTeX entries. Default: new line.
        self.entry_separator = '\n'

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
        for entry_id in sorted(bib_database.entries_dict.keys()):
            bibtex += self._entry_to_bibtex(bib_database.entries_dict[entry_id])
        return bibtex

    def _entry_to_bibtex(self, entry):
        bibtex = ''
        # Write BibTeX key
        bibtex += '@' + entry['type'] + '{' + entry['id']

        # Write field = value lines
        for field in [i for i in sorted(entry) if i not in ['type', 'id']]:
            try:
                bibtex += ",\n" + self.indent + field + " = {" + entry[field] + "}"
            except TypeError:
                raise TypeError("The field %s in entry %s must be a string"
                                % (field, entry['id']))
        bibtex += "\n}\n" + self.entry_separator
        return bibtex

    def _comments_to_bibtex(self, bib_database):
        bibtex = ''
        for comment in bib_database.comments:
            bibtex += "@comment{{{0}}}\n{1}".format(comment, self.entry_separator)
        return bibtex

    def _preambles_to_bibtex(self, bib_database):
        # TODO: implement preamble writing
        raise NotImplementedError

    def _strings_to_bibtex(self, bib_database):
        # TODO: implement string definitions writing
        raise NotImplementedError

