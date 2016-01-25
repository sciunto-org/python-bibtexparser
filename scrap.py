import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
from bibtexparser.bwriter import *


def arx(record):
    record = arxiv_pdf(record)
    return record

with open('bibtexparser/tests/data/arxiv_pdf.bib') as bibtex_file:

    parser = BibTexParser()
    parser.customization = arx
    bib_database = bibtexparser.load(bibtex_file, parser=parser)
    print(bib_database.entries)