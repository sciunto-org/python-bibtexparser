"""
Bibtexparser Module

Parser for bibtex files.
"""
__all__ = ['bparser', 'bwrite', 'info', 'latexenc', 'customization']
__version__ = '0.5.5'

from . import bparser, bwriter, info, latexenc, customization


def loads(bibtex_str, parser_cls=None):
    if parser_cls is None:
        parser_cls = bparser.BibTexParser
    return parser_cls().parse(bibtex_str)


def load(bibtex_file, parser_cls=None):
    if parser_cls is None:
        parser_cls = bparser.BibTexParser
    return parser_cls().parse_file(bibtex_file)


def dumps(bib_database, writer_cls=None):
    if writer_cls is not None:
        raise NotImplementedError
        # TODO: make bwriter into a class
    return bwriter.to_bibtex(bib_database)