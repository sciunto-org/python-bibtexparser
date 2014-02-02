#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Original source: github.com/okfn/bibserver
# Authors:
# markmacgillivray
# Etienne Posthumus (epoz)
# Francois Boulogne <fboulogne at april dot org>

import sys
import logging

logger = logging.getLogger(__name__)

__all__ = ['BibTexParser']


if sys.version_info >= (3, 0):
    from io import StringIO
    ustr = str
else:
    from StringIO import StringIO
    ustr = unicode


class BibTexParser(object):
    """
    A parser for bibtex files.

    By default (i.e. without customizations), each value in entries are considered
    as a string.

    :param fileobj: a filehandler
    :param customization: a function

    Example:

    >>> from bibtexparser.bparser import BibTexParser
    >>> filehandler = open('bibtex', 'r')
    >>> parser = BibTexParser(filehandler)
    >>> record_list = parser.get_entry_list()
    >>> records_dict = parser.get_entry_dict()

    """
    def __init__(self, fileobj, customization=None):
        data = fileobj.read()

        # On some sample data files, the character encoding detection simply hangs
        # We are going to default to utf8, and mandate it.
        self.encoding = 'utf8'

        # Some files have Byte-order marks inserted at the start
        if data[:3] == '\xef\xbb\xbf':
            data = data[3:]
        self.fileobj = StringIO(data)

        # set which bibjson schema this parser parses to
        self.has_metadata = False
        self.persons = []
        # if bibtex file has substition strings, they are stored here,
        # then the values are checked for those substitions in _add_val
        self.replace_dict = {}
        # pre-defined set of key changes
        self.alt_dict = {
            'keyw': 'keyword',
            'keywords': 'keyword',
            'authors': 'author',
            'editors': 'editor',
            'url': 'link',
            'urls': 'link',
            'links': 'link',
            'subjects': 'subject'
        }

        self.records = self._parse_records(customization=customization)
        self.entries_hash = {}

    def get_entry_list(self):
        """Get a list of bibtex entries.

        :retuns: list -- entries
        """
        return self.records

    def get_entry_dict(self):
        """Get a dictionnary of bibtex entries.
        The dict key is the bibtex entry key

        :retuns: dict -- entries
        """
        # If the hash has never been made, make it
        if not self.entries_hash:
            for entry in self.records:
                self.entries_hash[entry['id']] = entry
        return self.entries_hash

    def _parse_records(self, customization=None):
        """Parse the bibtex into a list of records.

        :param customization: a function
        :returns: list -- records
        """
        def _add_parsed_record(record, records):
            """
            Atomic function to parse a record
            and append the result in records
            """
            if record != "":
                logger.debug('The record is not empty. Let\'s parse it.')
                parsed = self._parse_record(record, customization=customization)
                if parsed:
                    logger.debug('Store the result of the parsed record')
                    records.append(parsed)
                else:
                    logger.debug('Nothing returned from the parsed record!')
            else:
                logger.debug('The record is empty')

        records = []
        record = ""
        # read each line, bundle them up until they form an object, then send for parsing
        for linenumber, line in enumerate(self.fileobj):
            logger.debug('Inspect line %s', linenumber)
            if '--BREAK--' in line:
                logger.debug('--BREAK-- encountered')
                break
            else:
                if line.strip().startswith('@'):
                    logger.debug('Line starts with @')
                    _add_parsed_record(record, records)
                    logger.debug('The record is set to empty')
                    record = ""
                if len(line.strip()) > 0:
                    logger.debug('The line is not empty, add it to record')
                    record += line

        # catch any remaining record and send it for parsing
        _add_parsed_record(record, records)
        logger.debug('Return the result')
        return records

    def _parse_record(self, record, customization=None):
        """Parse a record.

        * tidy whitespace and other rubbish
        * parse out the bibtype and citekey
        * find all the key-value pairs it contains

        :param record: a record
        :param customization: a function

        :returns: dict --
        """
        d = {}

        if not record.startswith('@'):
            logger.debug('The record does not start with @. Return empty dict.')
            return {}

        # prepare record
        record = '\n'.join([i.strip() for i in record.split('\n')])
        if '}\n' in record:
            record, rubbish = record.replace('\r\n', '\n').replace('\r', '\n').rsplit('}\n', 1)

        # if a string record, put it in the replace_dict
        if record.lower().startswith('@string'):
            logger.debug('The record startswith @string')
            key, val = [i.strip().strip('"').strip('{').strip('}').replace('\n', ' ') for i in record.split('{', 1)[1].strip('\n').strip(',').strip('}').split('=')]
            self.replace_dict[key] = val
            logger.debug('Return a dict')
            return d

        # for each line in record
        logger.debug('Split the record of its lines and treat them')
        kvs = [i.strip() for i in record.split(',\n')]
        inkey = ""
        inval = ""
        for kv in kvs:
            logger.debug('Inspect: %s', kv)
            if kv.startswith('@') and not inkey:
                # it is the start of the record - set the bibtype and citekey (id)
                logger.debug('Line starts with @ and the key is not stored yet.')
                bibtype, id = kv.split('{', 1)
                bibtype = self._add_key(bibtype)
                id = id.strip('}').strip(',')
            elif '=' in kv and not inkey:
                # it is a line with a key value pair on it
                logger.debug('Line contains a key-pair value and the key is not stored yet.')
                key, val = [i.strip() for i in kv.split('=', 1)]
                key = self._add_key(key)
                # if it looks like the value spans lines, store details for next loop
                if (val.count('{') != val.count('}')) or (val.startswith('"') and not val.replace('}', '').endswith('"')):
                    logger.debug('The line is not ending the record.')
                    inkey = key
                    inval = val
                else:
                    logger.debug('The line is the end of the record.')
                    d[key] = self._add_val(val)
            elif inkey:
                logger.debug('Continues the previous line to complete the key pair value...')
                # if this line continues the value from a previous line, append
                inval += ', ' + kv
                # if it looks like this line finishes the value, store it and clear for next loop
                if (inval.startswith('{') and inval.endswith('}')) or (inval.startswith('"') and inval.endswith('"')):
                    logger.debug('This line represents the end of the current key-pair value')
                    d[inkey] = self._add_val(inval)
                    inkey = ""
                    inval = ""
                else:
                    logger.debug('This line does NOT represent the end of the current key-pair value')

        logger.debug('All lines have been treated')
        if not d:
            logger.debug('The dict is empty, return it.')
            return d

        # put author names into persons list
        if 'author_data' in d:
            self.persons = [i for i in d['author_data'].split('\n')]
            del d['author_data']

        d['type'] = bibtype
        d['id'] = id
        if not self.has_metadata and 'type' in d:
            if d['type'] == 'personal bibliography' or d['type'] == 'comment':
                self.has_metadata = True

        if customization is None:
            logger.debug('No customization to apply, return dict')
            return d
        else:
            # apply any customizations to the record object then return it
            logger.debug('Apply customizations and return dict')
            return customization(d)

    def _strip_quotes(self, val):
        """Strip double quotes enclosing string

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        return val

    def _strip_braces(self, val):
        """Strip braces enclosing string

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        val.strip()
        if val.startswith('{') and val.endswith('}'):
            return val[1:-1]
        return val

    def _string_subst(self, val):
        """ Substitute string definitions

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        if not val:
            return ''
        for k in list(self.replace_dict.keys()):
            if val == k:
                val = self.replace_dict[k]
        if not isinstance(val, ustr):
            val = ustr(val, self.encoding, 'ignore')

        return val

    def _add_val(self, val):
        """ Clean instring before adding to dictionary

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        if not val or val == "{}":
            return ''
        val = self._strip_braces(val)
        val = self._strip_quotes(val)
        val = self._strip_braces(val)
        val = self._string_subst(val)
        return val

    def _add_key(self, key):
        """ Add a key and homogeneize alternative forms.

        :param key: a key
        :type key: string
        :returns: string -- value
        """
        key = key.strip().strip('@').lower()
        if key in list(self.alt_dict.keys()):
            key = self.alt_dict[key]
        if not isinstance(key, ustr):
            return ustr(key, 'utf-8')
        else:
            return key
