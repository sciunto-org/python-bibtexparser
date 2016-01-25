#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A set of functions useful for customizing bibtex fields.
You can find inspiration from these functions to design yours.
Each of them takes a record and return the modified record.
"""

import itertools
import re
import logging
import string
import requests
import feedparser

from bibtexparser.latexenc import unicode_to_latex, unicode_to_crappy_latex1, unicode_to_crappy_latex2, string_to_latex, protect_uppercase


logger = logging.getLogger(__name__)

__all__ = ['getnames', 'author', 'author_order', 'editor', 'journal', 'keyword', 'link',
           'page_double_hyphen', 'doi', 'type', 'convert_to_unicode',
           'homogeneize_latex_encoding', 'citation_key', 'arxiv_pdf']

def getnames(names):
    """Make people names as surname, firstnames
    or surname, initials. Should eventually combine up the two.

    :param names: a list of names
    :type names: list
    :returns: list -- Correctly formatted names
    """
    tidynames = []
    for namestring in names:
        namestring = namestring.strip()
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        else:
            namesplit = namestring.split()
            last = namesplit.pop()
            firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()
        for item in firsts:
            if item in ['ben', 'van', 'der', 'de', 'la', 'le']:
                last = firsts.pop() + ' ' + last
        tidynames.append(last + ", " + ' '.join(firsts))
    return tidynames

def citation_key(record):
    """
    Generates citation key for a record.

    :param record: the record
    :return: modified record, i.e. with citation key
    """

    # add arxiv to entries without doi?
    # not consistent: cf @InProceedings{ABDR04} in quantum bib

    record_copy = dict()
    for key in record:
        record_copy[key] = record[key]

    # handle special characters correctly for citation key without affecting author field
    record_copy = convert_to_unicode(record_copy)

    names = []
    if "author" in record_copy:
        if isinstance(record_copy["author"], list):
            names = record_copy["author"]
        else:
            names = getnames([i.strip() for i in record_copy["author"].replace('\n', ' ').split(" and ")])

    lastnames = []

    # from getnames function
    for namestring in names:
        namestring = namestring.strip()
        namestring = re.sub('[{}\/]', '', namestring)
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        else:
            namesplit = namestring.split()
            last = namesplit.pop()
            firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()
        for item in firsts:
            if item in ['ben', 'van', 'der', 'de', 'la', 'le']:
                last = firsts.pop() + ' ' + last
        lastnames.append(last)

    letters_accent = ['á', 'ä', 'â', 'à', 'é', 'ë', 'ê', 'è',
                      'í', 'ï', 'ì', 'ó', 'ö', 'ô', 'ò', 'ú', 'ü', 'û', 'ù']

    # generate citation key
    if "year" in record_copy:
        year = record_copy["year"]
        years = year[2:]

        def get_initials(name, one_author):
            """
            name is a string, one_author boolean
            """

            name = name.split(' ')
            initials = ''
            i = 0

            # handle van/von/der etc. correctly
            while name[i][0] in string.ascii_lowercase:
                initials += name[i][0]
                i += 1
            if one_author == True:
                beginning_name = ''
                letter_count = 0
                j = 0
                # make sure that citation key only contains alphabetic characters, so no accents,
                # and that it always contains three characters in case of single author
                while letter_count < 3:
                    beginning_name += name[i][j]
                    if (name[i][j] in string.ascii_letters) or (name[i][j] in letters_accent):
                        letter_count += 1
                    j += 1
                initials += beginning_name
            else:
                initials += name[i][0]
            return initials

        if len(lastnames) == 1:
            author = lastnames[0]
            beginning = get_initials(author, True)
            key = beginning + years
        else:
            initials = ''
            if len(lastnames) <= 4:
                for name in lastnames:
                    initials += get_initials(name, False)
            else:
                for i in [0, 1, 2]:
                    initials += get_initials(lastnames[i][0], False)
                initials += '+'
            key = initials + years

        record["alphakey"] = key
    return record

def author(record):
    """
    Split author field into a list of "Name, Surname".

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "author" in record:
        if record["author"]:
            record["author"] = getnames([i.strip() for i in record["author"].replace('\n', ' ').split(" and ")])
        else:
            del record["author"]
    return record

def author_order(record):
    """
    Writes authors as 'Surname, Name' without changing type (string).

    :param record: the record
    :return: modified record
    """
    names = []
    if "author" in record:
        if isinstance(record["author"], list):
            names = record["author"]
        else:
            names = getnames([i.strip() for i in record["author"].replace('\n', ' ').split(" and ")])

    new_name = ''
    for name in names:
        new_name += name + ' and '
    length = len(new_name)
    new_name = new_name[0:length-5]
    record['author'] = new_name
    return record

def editor(record):
    """
    Turn the editor field into a dict composed of the original editor name
    and a editor id (without coma or blank).

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "editor" in record:
        if record["editor"]:
            record["editor"] = getnames([i.strip() for i in record["editor"].replace('\n', ' ').split(" and ")])
            # convert editor to object
            record["editor"] = [{"name": i, "ID": i.replace(',', '').replace(' ', '').replace('.', '')} for i in record["editor"]]
        else:
            del record["editor"]
    return record


def page_double_hyphen(record):
    """
    Separate pages by a double hyphen (--).

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "pages" in record:
        # hyphen, non-breaking hyphen, en dash, em dash, hyphen-minus, minus sign
        separators = [u'‐', u'‑', u'–', u'—', u'-', u'−']
        for separator in separators:
            if separator in record["pages"]:
                p = [i.strip().strip(separator) for i in record["pages"].split(separator)]
                record["pages"] = p[0] + '--' + p[-1]
    return record


def type(record):
    """
    Put the type into lower case.

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "type" in record:
        record["type"] = record["type"].lower()
    return record


def journal(record):
    """
    Turn the journal field into a dict composed of the original journal name
    and a journal id (without coma or blank).

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "journal" in record:
        # switch journal to object
        if record["journal"]:
            record["journal"] = {"name": record["journal"], "ID": record["journal"].replace(',', '').replace(' ', '').replace('.', '')}

    return record


def keyword(record, sep=',|;'):
    """
    Split keyword field into a list.

    :param record: the record.
    :type record: dict
    :param sep: pattern used for the splitting regexp.
    :type record: string, optional
    :returns: dict -- the modified record.

    """
    if "keyword" in record:
        record["keyword"] = [i.strip() for i in re.split(sep, record["keyword"].replace('\n', ''))]

    return record


def link(record):
    """

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "link" in record:
        links = [i.strip().replace("  ", " ") for i in record["link"].split('\n')]
        record['link'] = []
        for link in links:
            parts = link.split(" ")
            linkobj = {"url": parts[0]}
            if len(parts) > 1:
                linkobj["anchor"] = parts[1]
            if len(parts) > 2:
                linkobj["format"] = parts[2]
            if len(linkobj["url"]) > 0:
                record["link"].append(linkobj)

    return record

def doi(record):
    """

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if 'doi' in record:
        if 'link' not in record:
            record['link'] = []
        nodoi = True
        for item in record['link']:
            if 'doi' in item:
                nodoi = False
        if nodoi:
            link = record['doi']
            if link.startswith('10'):
                link = 'http://dx.doi.org/' + link
            record['link'].append({"url": link, "anchor": "doi"})
    return record


def convert_to_unicode(record):
    """
    Convert accent from latex to unicode style.

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.
    """
    for val in record:
        if '\\' in record[val] or '{' in record[val]:
            for k, v in itertools.chain(unicode_to_crappy_latex1, unicode_to_latex):
                if v in record[val]:
                    record[val] = record[val].replace(v, k)

        # If there is still very crappy items
        if '\\' in record[val]:
            for k, v in unicode_to_crappy_latex2:
                if v in record[val]:
                    parts = record[val].split(str(v))
                    for key, record[val] in enumerate(parts):
                        if key+1 < len(parts) and len(parts[key+1]) > 0:
                            # Change order to display accents
                            parts[key] = parts[key] + parts[key+1][0]
                            parts[key+1] = parts[key+1][1:]
                    record[val] = k.join(parts)
    return record


def homogeneize_latex_encoding(record):
    """
    Homogeneize the latex enconding style for bibtex

    This function is experimental.

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.
    """
    # First, we convert everything to unicode
    record = convert_to_unicode(record)
    # And then, we fall back
    for val in record:
        if val not in ('ID',):
            logger.debug('Apply string_to_latex to: %s', val)
            record[val] = string_to_latex(record[val])
            if val == 'title':
                logger.debug('Protect uppercase in title')
                logger.debug('Before: %s', record[val])
                record[val] = protect_uppercase(record[val])
                logger.debug('After: %s', record[val])
    return record

def arxiv_pdf(record):
    """
    Retrieve link to Arxiv pdf, if available. Uses Arxiv API.

    :param record:
    :return: record with link to arxiv pdf, if available
    """

    query = ''
    if 'title' in record:
        title = record['title']
        title_convert = title.replace ("-", " ")
        title_convert = title_convert.replace("+", " ")

        for word in title_convert.split():
            word = word.lower()

            if word not in ['and', 'not', 'or']:
                query += word
                query += '+AND+'

        if 'author' in record:
            author = record['author']

            author = author.replace("and", "").replace("\\", "").replace("'", "").replace("\"", "")
            author = re.sub('[{}\/]', '', author)
            author = author.split()

            for name in author:
                length_name = len(name)
                if name[length_name-1] != '.':
                    query += name
                    query += '+AND+'
            length = len(query)
            end = length - 5

            # remove final '+'
            query = query[0:end]

            result = requests.get('http://export.arxiv.org/api/'
                                  'query?search_query=all:' + query +
                                  '&start=0&max_results=1')

            result = result.text
            feed = feedparser.parse(result)
            title_found = ''
            for entry in feed.entries:
                title_found = entry.title
            title_found = title_found.replace("  ", " ")
            title_found = title_found.replace("\n", "")
            if (title_found == title):
                for link in entry.links:
                    if link.type == 'application/pdf':
                        pdf_link = link.href
                        record["arxiv_pdf"] = pdf_link
    return record

def get_editors(record):
    """
    Retrieve authors of an edited publication.

    :param record:
    :return:
    """

    if 'doi' in record:
        doi = record['doi']

        link = 'http://api.crossref.org/works/works/' + doi
        r = requests.get(link)

        info = r.json()

        # get editors, but is this necessary?

