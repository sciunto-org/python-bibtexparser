"""
BibTeX <http://en.wikipedia.org/wiki/BibTeX> is a bibliographic data file format.

The :mod:`bibtexparser` module provides parsing and writing of BibTeX files functionality. The API is similar to the
:mod:`json` module. The parsed data is returned as a simple :class:`BibDatabase` object with the main attribute being
:attr:`entries` representing bibliographic sources such as books and journal articles.

Parsing is a simple as::

    >>>> import bibtexparser
    >>>> with open('bibtex.bib') as bibtex_file:
    >>>>    bibtex_database = bibtexparser.load(bibtex_file)

And writing::

    >>>> import bibtexparser
    >>>> with open('bibtex.bib', 'w') as bibtex_file:
    >>>>     bibtexparser.dump(bibtex_database, bibtex_file)

"""
__all__ = [
    'loads', 'load', 'dumps', 'dump', 'bibdatabase',
    'bparser', 'bwriter', 'latexenc', 'customization',
]
__version__ = '0.6.1'

from . import bibdatabase, bparser, bwriter, latexenc, customization


def loads(bibtex_str, parser=None):
    """
    Load :class:`BibDatabase` object from a string

    :param bibtex_str: input BibTeX string to be parsed
    :type bibtex_str: str or unicode
    :param parser: custom parser to use (optional)
    :type parser: BibTexParser
    :return: bibliographic database object
    :rtype: BibDatabase
    """
    if parser is None:
        parser = bparser.BibTexParser()
    return parser.parse(bibtex_str)


def load(bibtex_file, parser=None):
    """
    Load :class:`BibDatabase` object from a file

    :param bibtex_file: input file to be parsed
    :type bibtex_file: file
    :param parser: custom parser to use (optional)
    :type parser: BibTexParser
    :return: bibliographic database object
    :rtype: BibDatabase
    """
    if parser is None:
        parser = bparser.BibTexParser()
    return parser.parse_file(bibtex_file)


def dumps(bib_database, writer=None):
    """
    Dump :class:`BibDatabase` object to a BibTeX string

    :param bib_database: bibliographic database object
    :type bib_database: BibDatabase
    :param writer: custom writer to use (optional) (not yet implemented)
    :type writer: BibTexWriter
    :return: BibTeX string
    :rtype: unicode
    """
    if writer is None:
        writer = bwriter.BibTexWriter()
    return writer.write(bib_database)


def dump(bib_database, bibtex_file, writer=None):
    """
    Save :class:`BibDatabase` object as a BibTeX text file

    :param bib_database: bibliographic database object
    :type bib_database: BibDatabase
    :param bibtex_file: file to write to
    :type bibtex_file: file
    :param writer: custom writer to use (optional) (not yet implemented)
    :type writer: BibTexWriter
    """
    if writer is None:
        writer = bwriter.BibTexWriter()
    bibtex_file.write(writer.write(bib_database))
