#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Original source: github.com/okfn/bibserver
# Authors:
# markmacgillivray
# Etienne Posthumus (epoz)
# Francois Boulogne <fboulogne at april dot org>

import sys
import logging
import pyparsing as pp
from .bibdatabase import BibDatabase, BibDataString, STANDARD_TYPES

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
    A parser for reading BibTeX bibliographic data files.

    Example::

        from bibtexparser.bparser import BibTexParser

        bibtex_str = ...

        parser = BibTexParser()
        parser.ignore_nonstandard_types = False
        parser.homogenise_fields = False
        bib_database = bibtexparser.loads(bibtex_str, parser)
    """

    def __new__(cls, data=None,
                customization=None,
                ignore_nonstandard_types=True,
                homogenise_fields=True):
        """
        To catch the old API structure in which creating the parser would immediately parse and return data.
        """

        if data is None:
            return super(BibTexParser, cls).__new__(cls)
        else:
            # For backwards compatibility: if data is given, parse and return the `BibDatabase` object instead of the
            # parser.
            parser = BibTexParser()
            parser.customization = customization
            parser.ignore_nonstandard_types = ignore_nonstandard_types
            parser.homogenise_fields = homogenise_fields
            return parser.parse(data)

    def __init__(self):
        """
        Creates a parser for rading BibTeX files

        :return: parser
        :rtype: `BibTexParser`
        """
        self.bib_database = BibDatabase()
        #: Callback function to process BibTeX entries after parsing, for example to create a list from a string with
        #: multiple values. By default all BibTeX values are treated as simple strings. Default: `None`.
        self.customization = None

        #: Ignore non-standard BibTeX types (`book`, `article`, etc). Default: `True`.
        self.ignore_nonstandard_types = True

        #: Sanitise BibTeX field names, for example change `url` to `link` etc. Field names are always converted to
        #: lowercase names. Default: `True`.
        self.homogenise_fields = True

        # On some sample data files, the character encoding detection simply
        # hangs We are going to default to utf8, and mandate it.
        self.encoding = 'utf8'

        # pre-defined set of key changes
        self.alt_dict = {
            'keyw': u'keyword',
            'keywords': u'keyword',
            'authors': u'author',
            'editors': u'editor',
            'url': u'link',
            'urls': u'link',
            'links': u'link',
            'subjects': u'subject'
        }

        self._init_expressions()

    def _init_expressions(self):
        """
        Defines all parser expressions used internally.
        """

        def first_token(s, l, t):
            # TODO Handle this case correctly!
            assert(len(t) == 1)
            return t[0]

        def remove_braces(s, l, t):
            if len(t[0]) < 1:
                return ''
            else:
                start = 1 if t[0][0] == '{' else 0
                end = -1 if t[0][-1] == '}' else None
                return t[0][start:end]

        string_def_start = pp.CaselessKeyword("@string")
        preamble_start = pp.CaselessKeyword("@preamble")
        comment_line_start = pp.CaselessKeyword('@comment')

        def in_braces_or_pars(exp):
            """
            exp -> (exp)|{exp}
            """
            return ((pp.Suppress('{') + exp + pp.Suppress('}')) |
                    (pp.Suppress('(') + exp + pp.Suppress(')')))

        # Values

        integer = pp.Word(pp.nums)('Integer')

        braced_value_content = pp.CharsNotIn('{}')
        braced_value = pp.Forward()
        braced_value <<= pp.originalTextFor(
            '{' + pp.ZeroOrMore(braced_value | braced_value_content) + '}'
            )('BracedValue')
        braced_value.setParseAction(remove_braces)
        # TODO add ignore for "\}" and "\{" ?
        # TODO @ are not parsed by bibtex in braces

        brace_in_quoted = pp.nestedExpr('{', '}')
        text_in_quoted = pp.Word(pp.printables, excludeChars='"{}')
        quoted_value = pp.originalTextFor(
            '"' +
            pp.ZeroOrMore(text_in_quoted | brace_in_quoted) +
            '"')('QuotedValue')
        quoted_value.addParseAction(pp.removeQuotes)
        # TODO Make sure that content is escaped with quotes when contains '@'

        string_name = pp.Word(pp.alphanums + '_')('StringName')
        string_name.setParseAction(lambda s, l, t:
            BibDataString(self.bib_database, t[0]))
        string_expr = pp.delimitedList(
            (quoted_value | braced_value | string_name), delim='#'
            )('StringExpression')
        # TODO Rather return an object to represent values and string
        # interpolation
        string_expr.setParseAction(lambda s, l, t:
            self._interpolate_string_expression(t))

        value = (integer | string_expr)('Value')

        # Entries

        entry_type = (pp.Suppress('@') + pp.Word(pp.alphas))('EntryType')
        entry_type.setParseAction(first_token)

        key = pp.SkipTo(',')('Key')  # Exclude @',\#}{~%
        key.setParseAction(lambda s, l, t: first_token(s, l, t).strip())

        field_name = pp.Word(pp.alphas)('FieldName')
        field_name.setParseAction(first_token)
        field = pp.Group(field_name + pp.Suppress('=') + value)('Field')

        # Not sure this is desirable but it is for conformance to previous
        # implementation
        def strip_after_new_lines(s):
            lines = s.splitlines()
            if len(lines) > 1:
                lines = [lines[0]] + [l.lstrip() for l in lines[1:]]
            return '\n'.join(lines)

        def field_to_pair(s, l, t):
            """
            Looks for parsed element named 'Field'.
            :returns: (name, value).
            """
            f = t.get('Field')
            return (f.get('FieldName'),
                    strip_after_new_lines(f.get('Value')))

        field.setParseAction(field_to_pair)

        field_list = (pp.delimitedList(field) + pp.Suppress(pp.Optional(','))
                      )('Fields')
        field_list.setParseAction(
            lambda s, l, t: {k: v for (k, v) in reversed(t.get('Fields'))})

        entry = (entry_type +
                 in_braces_or_pars(key + pp.Suppress(',') + field_list)
                 )('Entry')

        # Other stuff

        implicit_comment_line = pp.originalTextFor(pp.SkipTo('\n'),
                                                   asString=True)
        explicit_comment_line = (pp.Suppress(comment_line_start) +
                                 implicit_comment_line)('Comment')
        explicit_comment_line.setParseAction(remove_braces)
        # Previous implementation included comment until next '}'.
        # This is however not inline with bibtex behavior that is to only
        # ignore until EOL. Brace stipping is arbitrary here but avoids
        # duplication on bibtex write.

        string_def = (pp.Suppress(string_def_start) + in_braces_or_pars(
            string_name + pp.Suppress('=') + string_expr('StringValue')
            ))('StringDefinition')
        preamble_decl = (pp.Suppress(preamble_start) +
                         in_braces_or_pars(value))('PreambleDeclaration')

        self._bibfile_expression = pp.ZeroOrMore(
                string_def |
                preamble_decl |
                explicit_comment_line |
                entry |
                implicit_comment_line)

        # Set actions
        entry.setParseAction(lambda s, l, t: self._add_entry(
            t.get('EntryType'), t.get('Key'), t.get('Fields')))
        implicit_comment_line.addParseAction(lambda s, l, t:
                                             self._add_comment(t[0]))
        explicit_comment_line.addParseAction(lambda s, l, t:
                                             self._add_comment(t[0]))
        preamble_decl.setParseAction(lambda s, l, t:
                                     self._add_preamble(t[0]))
        string_def.setParseAction(lambda s, l, t:
                                  self._add_string(t['StringName'].name,
                                                   t['StringValue']))

    def _bibtex_file_obj(self, bibtex_str):
        # Some files have Byte-order marks inserted at the start
        byte = '\xef\xbb\xbf'
        if not isinstance(byte, ustr):
            byte = ustr('\xef\xbb\xbf', self.encoding, 'ignore')
        if bibtex_str[:3] == byte:
            bibtex_str = bibtex_str[3:]
        return StringIO(bibtex_str)

    def parse(self, bibtex_str, partial=True):
        """Parse a BibTeX string into an object

        :param bibtex_str: BibTeX string
        :type: str or unicode
        :param partial: if False fails on incomplete parse
        :type: boolean
        :return: bibliographic database
        :rtype: BibDatabase
        """
        bibtex_file_obj = self._bibtex_file_obj(bibtex_str)
        try:
            self._bibfile_expression.parseFile(bibtex_file_obj, parseAll=True)
        except pp.ParseException as exc:
            logger.warning("Could not parse full file or string.")
            if not partial:
                raise exc
        return self.bib_database

    def parse_file(self, file, partial=True):
        """Parse a BibTeX file into an object

        :param file: BibTeX file or file-like object
        :type: file
        :param partial: if False fails on incomplete parse
        :type: boolean
        :return: bibliographic database
        :rtype: BibDatabase
        """
        return self.parse(file.read(), partial=partial)


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
        if val.startswith('{') and val.endswith('}') and self._full_span(val):
            return val[1:-1]
        return val

    def _full_span(self, val):
        cnt = 0
        for i in range(0, len(val)):
                if val[i] == '{':
                        cnt += 1
                elif val[i] == '}':
                        cnt -= 1
                if cnt == 0:
                        break
        if i == len(val) - 1:
                return True
        else:
                return False

    def _clean_val(self, val):
        """ Clean instring before adding to dictionary

        :param val: a value
        :type val: string
        :returns: string -- value
        """
        if not val or val == "{}":
            return ''
        return val

    def _clean_key(self, key):
        """ Lowercase a key and return as unicode.

        :param key: a key
        :type key: string
        :returns: (unicode) string -- value
        """
        key = key.lower()
        if not isinstance(key, ustr):
            return ustr(key, 'utf-8')
        else:
            return key

    def _clean_field_key(self, key):
        """ Clean a bibtex field key and homogeneize alternative forms.

        :param key: a key
        :type key: string
        :returns: string -- value
        """
        key = self._clean_key(key)
        if self.homogenise_fields:
            if key in list(self.alt_dict.keys()):
                key = self.alt_dict[key]
        return key

    def _add_entry(self, entry_type, entry_id, fields):
        """ Adds a parsed entry.
        Includes checking type and fields, cleaning, applying customizations.

        :param entry_type: the entry type
        :type entry_type: string
        :param entry_id: the entry bibid
        :type entry_id: string
        :param fields: the fileds and values
        :type fields: dictionary
        :returns: string -- value
        """
        d = {}
        entry_type = self._clean_key(entry_type)
        if self.ignore_nonstandard_types and entry_type not in STANDARD_TYPES:
            logger.warning('Entry type %s not standard. Not considered.',
                           entry_type)
            return
        for key in fields:
            d[self._clean_field_key(key)] = self._clean_val(fields[key])
        d['ENTRYTYPE'] = entry_type
        d['ID'] = entry_id
        if self.customization is not None:
            # apply any customizations to the record object then return it
            logger.debug('Apply customizations and return dict')
            d = self.customization(d)
        self.bib_database.entries.append(d)

    def _add_comment(self, comment):
        """
        Stores a comment in the list of comment.

        :param comment: the parsed comment
        :type comment: string
        """
        logger.debug('Store comment in list of comments')
        self.bib_database.comments.append(comment)

    def _add_string(self, string_key, string):
        """
        Stores a new string in the string dictionary.

        :param string_key: the string key
        :type string_key: string
        :param string: the string value
        :type string: string
        """
        if string_key in self.bib_database.strings:
            logger.warning('Overwritting existing string for key: %s.',
                           string_key)
        logger.debug('Store string: {} -> {}'.format(string_key, string))
        self.bib_database.strings[string_key] = self._clean_val(string)

    def _interpolate_string_expression(self, string_expr):
        """
        Replaces bibdatastrings by their values in an expression.

        :param string_expr: the parsed string as a list
        :type string_expr: list
        """
        return ''.join([self._expand_string(s) for s in string_expr])

    def _expand_string(self, string_or_bibdatastring):
        """
        Eventually replaces a bibdatastring by its value.

        :param string_or_bibdatastring: the parsed token
        :type string_expr: string or BibDataString
        :returns: string
        """
        if isinstance(string_or_bibdatastring, BibDataString):
            return string_or_bibdatastring.get_value()
        else:
            return string_or_bibdatastring

    def _add_preamble(self, preamble):
        """
        Stores a preamble.

        :param preamble: the parsed preamble
        :type preamble: string
        """
        logger.debug('Store preamble in list of preambles')
        self.bib_database.preambles.append(preamble)
