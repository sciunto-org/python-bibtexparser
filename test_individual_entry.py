import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
from bibtexparser.bwriter import *

# Let's define a function to customize our entries.
# It takes a record and return this record.
def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """

    # certain customizations affect bibdatabases but do not translate
    # back to bibtex format, namely the commented ones below

    record = type(record)
    #record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)

    #record = link(record)

    record = page_double_hyphen(record)
    record = doi(record)
    record = citation_key(record)
    return record

def key(record):
    record = citation_key(record)
    return record

with open('random.bib') as bibtex_file:

    parser = BibTexParser()
    parser.customization = key
    bib_database = bibtexparser.load(bibtex_file, parser=parser)
    print(bib_database.entries)

"""
with open('bibtexparser/tests/data/random.bib') as bibtex_file:
    parser2 = BibTexParser()
    parser2.customization = both
    bib_database2 = bibtexparser.load(bibtex_file, parser=parser2)
    print(bib_database2.entries)


writer = BibTexWriter()
with open('bibtexparser/tests/data/random.bib', 'w') as bibfile:

    writer.align_values = True
    writer.contents = ['comments', 'entries']
    writer.indent = '  '
    writer.order_entries_by = ('ENTRYTYPE', 'author', 'year')

    bibtex_str = bibtexparser.dumps(bib_database, writer)
    bibfile.write(bibtex_str)
"""