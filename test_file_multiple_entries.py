# 'clean' a bibtex file in its entirety, adding automatically generated alphakeys to entries

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
from bibtexparser.bwriter import *

# Let's define a function to customize our entries.
# It takes a record and return this record.

def add_alphakey(record):
    record = citation_key(record)
    return record

# hardwired file location

with open('bibtexparser/tests/data/citation_keys.bib', 'r') as bibtex_file:
    # list of bibtex entries

    parser = BibTexParser()
    parser.customization = add_alphakey
    bib_database = bibtexparser.load(bibtex_file, parser=parser)

    print(bib_database.entries)



"""
writer = BibTexWriter()
with open('bibtexparser/tests/data/messy_bibfile_output.bib', 'w') as bibfile:

    writer.align_values = True
    writer.contents = ['comments', 'entries']
    writer.indent = '  '
    writer.order_entries_by = ('ENTRYTYPE', 'author', 'year')

    bibtex_str = bibtexparser.dumps(bib_database, writer)
    bibfile.write(bibtex_str)

"""