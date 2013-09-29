#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Original source: github.com/okfn/bibserver
# Authors:
# markmacgillivray
# Etienne Posthumus (epoz)
# Francois Boulogne <fboulogne at april dot org>

import io

__all__ = ['BibTexParser']


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
        self.fileobj = io.StringIO(data)

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
        entries_hash = {}
        for entry in self.records:
            entries_hash[entry['id']] = entry
        return entries_hash

    def _parse_records(self, customization=None):
        """Parse the bibtex into a list of records.

        :param customization: a function
        :returns: list -- records
        """
        records = []
        record = ""
        # read each line, bundle them up until they form an object, then send for parsing
        for line in self.fileobj:
            if '--BREAK--' in line:
                break
            else:
                if line.strip().startswith('@'):
                    if record != "":
                        parsed = self._parse_record(record, customization=customization)
                        if parsed:
                            records.append(parsed)
                    record = ""
                if len(line.strip()) > 0:
                    record += line

        # catch any remaining record and send it for parsing
        if record != "":
            parsed = self._parse_record(record, customization=customization)
            if parsed:
                records.append(parsed)
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
            return d

        # prepare record
        record = '\n'.join([i.strip() for i in record.split('\n')])
        if '}\n' in record:
            record, rubbish = record.replace('\r\n', '\n').replace('\r', '\n').rsplit('}\n', 1)

        # if a string record, put it in the replace_dict
        if record.lower().startswith('@string'):
            key, val = [i.strip().strip('"').strip('{').strip('}').replace('\n', ' ') for i in record.split('{', 1)[1].strip('\n').strip(',').strip('}').split('=')]
            self.replace_dict[key] = val
            return d

        # for each line in record
        kvs = [i.strip() for i in record.split(',\n')]
        inkey = ""
        inval = ""
        for kv in kvs:
            if kv.startswith('@') and not inkey:
                # it is the start of the record - set the bibtype and citekey (id)
                bibtype, id = kv.split('{', 1)
                bibtype = self._add_key(bibtype)
                id = id.strip('}').strip(',')
            elif '=' in kv and not inkey:
                # it is a line with a key value pair on it
                key, val = [i.strip() for i in kv.split('=', 1)]
                key = self._add_key(key)
                # if it looks like the value spans lines, store details for next loop
                if (val.startswith('{') and not val.endswith('}')) or (val.startswith('"') and not val.replace('}', '').endswith('"')):
                    inkey = key
                    inval = val
                else:
                    d[key] = self._add_val(val)
            elif inkey:
                # if this line continues the value from a previous line, append
                inval += ',' + kv
                # if it looks like this line finishes the value, store it and clear for next loop
                if (inval.startswith('{') and inval.endswith('}')) or (inval.startswith('"') and inval.endswith('"')):
                    d[inkey] = self._add_val(inval)
                    inkey = ""
                    inval = ""

        # put author names into persons list
        if 'author_data' in d:
            self.persons = [i for i in d['author_data'].split('\n')]
            del d['author_data']

        if not d:
            return d

        d['type'] = bibtype
        d['id'] = id
        if not self.has_metadata and 'type' in d:
            if d['type'] == 'personal bibliography' or d['type'] == 'comment':
                self.has_metadata = True

        if customization is None:
            return d
        else:
            # apply any customizations to the record object then return it
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
        if not isinstance(val, str):
            val = str(val, self.encoding, 'ignore')

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
        if not isinstance(key, str):
            return str(key, 'utf-8')
        else:
            return key
