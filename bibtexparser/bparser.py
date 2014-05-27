#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Original source: github.com/okfn/bibserver
# Authors:
# markmacgillivray
# Etienne Posthumus (epoz)
# Francois Boulogne <fboulogne at april dot org>

import sys
import logging
import io
import re

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

    By default (i.e. without customizations), each value in entries are
    considered as a string.

    :param data: a string
    :param customization: a function to modify fields
    :param ignore_nonstandard_types: If true, do not check the validity of
    entries types (article, book...)

    Example:

    >>> from bibtexparser.bparser import BibTexParser
    >>> filehandler = open('bibtex', 'r')
    >>> parser = BibTexParser(filehandler.read())
    >>> record_list = parser.get_entry_list()
    >>> records_dict = parser.get_entry_dict()

    """
    def __init__(self, data, customization=None,
                 ignore_nonstandard_types=True):
        if type(data) is io.TextIOWrapper:
            logger.critical("The API has changed. You should pass data instead \
                             of a filehandler.")
            raise TypeError('Wrong type for data')

        # On some sample data files, the character encoding detection simply
        # hangs We are going to default to utf8, and mandate it.
        self.encoding = 'utf8'

        # Some files have Byte-order marks inserted at the start
        byte = '\xef\xbb\xbf'
        if not isinstance(byte, ustr):
            byte = ustr('\xef\xbb\xbf', self.encoding, 'ignore')
        if data[:3] == byte:
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
        self.ignore_nonstandard_types = ignore_nonstandard_types

        self.replace_all_re = re.compile(r'((?P<pre>"?)\s*(#|^)\s*(?P<id>[^\d\W]\w*)\s*(#|$)\s*(?P<post>"?))', re.UNICODE)

        self.records = self._parse_records(customization=customization)
        self.entries_hash = {}

    def get_entry_list(self):
        """Get a list of bibtex entries.

        :returns: list -- entries
        """
        return self.records

    def get_entry_dict(self):
        """Get a dictionnary of bibtex entries.
        The dict key is the bibtex entry key

        :returns: dict -- entries
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

        # if a preamble record, ignore it
        if record.lower().startswith('@preamble'):
            logger.debug('The record startswith @preamble')
            logger.debug('Return an empty dict')
            return {}

        # if a comment record, ignore it
        if record.lower().startswith('@comment'):
            logger.debug('The record startswith @comment')
            logger.debug('Return an empty dict')
            return {}

        # if a string record, put it in the replace_dict
        if record.lower().startswith('@string'):
            logger.debug('The record startswith @string')
            key, val = [i.strip().strip('{').strip('}').replace('\n', ' ') for i in record.split('{', 1)[1].strip('\n').strip(',').strip('}').split('=')]
            key = key.lower()  # key is case insensitive
            val = self._string_subst_partial(val)
            if val.startswith('"') or val.lower() not in self.replace_dict:
                self.replace_dict[key] = val.strip('"')
            else:
                self.replace_dict[key] = self.replace_dict[val.lower()]
            logger.debug('Return a dict')
            return d

        # for each line in record
        logger.debug('Split the record of its lines and treat them')
        kvs = [i.strip() for i in record.split(',\n')]
        inkey = ""
        inval = ""
        for kv in kvs:
            logger.debug('Inspect: %s', kv)
            # TODO: We may check that the keyword belongs to a known type
            if kv.startswith('@') and not inkey:
                # it is the start of the record - set the bibtype and citekey (id)
                logger.debug('Line starts with @ and the key is not stored yet.')
                bibtype, id = kv.split('{', 1)
                bibtype = self._add_key(bibtype)
                id = id.strip('}').strip(',')
                logger.debug('bibtype = %s', bibtype)
                logger.debug('id = %s', id)
                if self.ignore_nonstandard_types and bibtype not in ('article',
                                                                     'book',
                                                                     'booklet',
                                                                     'conference',
                                                                     'inbook',
                                                                     'incollection',
                                                                     'inproceedings',
                                                                     'manual',
                                                                     'mastersthesis',
                                                                     'misc',
                                                                     'phdthesis',
                                                                     'proceedings',
                                                                     'techreport',
                                                                     'unpublished'):
                    logger.warning('Entry type %s not standard. Not considered.', bibtype)
                    break
            elif '=' in kv and not inkey:
                # it is a line with a key value pair on it
                logger.debug('Line contains a key-pair value and the key is not stored yet.')
                key, val = [i.strip() for i in kv.split('=', 1)]
                key = self._add_key(key)
                val = self._string_subst_partial(val)
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
        logger.debug('Strip quotes')
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
        logger.debug('Strip braces')
        val = val.strip()
        if val.startswith('{') and val.endswith('}'):
            return val[1:-1]
        return val

    def _string_subst(self, val):
        """ Substitute string definitions

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        logger.debug('Substitute string definitions')
        if not val:
            return ''
        for k in list(self.replace_dict.keys()):
            if val.lower() == k:
                val = self.replace_dict[k]
        if not isinstance(val, ustr):
            val = ustr(val, self.encoding, 'ignore')

        return val

    def _string_subst_partial(self, val):
        """ Substitute string definitions inside larger expressions

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        def repl(m):
            k = m.group('id')
            replacement = self.replace_dict[k.lower()] if k.lower() in self.replace_dict else k
            pre = '"' if m.group('pre') != '"' else ''
            post = '"' if m.group('post') != '"' else ''
            return pre + replacement + post

        logger.debug('Substitute string definitions inside larger expressions')
        if '#' not in val:
            return val
    
        # TODO?: Does not match two subsequent variables or strings, such as  "start" # foo # bar # "end"  or  "start" # "end".
        # TODO:  Does not support braces instead of quotes, e.g.: {start} # foo # {bar}
        # TODO:  Does not support strings like: "te#s#t"        
        return self.replace_all_re.sub(repl, val)

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
