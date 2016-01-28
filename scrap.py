import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
from bibtexparser.bwriter import *
from bibtexparser.bibdatabase import BibDatabase

def arx(record):
    record = author_order(record)
    return record

def order(record):
    record = author_order(record)
    return record

def author(record):
    record = author(record)
    return record

def editors(record):
    record = get_editors(record)
    return record

with open('scrap.bib') as bibtex_file:

    parser = BibTexParser()
    parser.customization = editors
    bib_database = bibtexparser.load(bibtex_file, parser=parser)
    print(bib_database.entries)


"""

db = BibDatabase()
    db.entries = bib_database.entries
    writer = BibTexWriter()
    with open('scrap2.bib', 'w') as bibfile:
        bibfile.write(writer.write(db))


names = ['Foo Bar',
                 'Foo B. Bar',
                 'F. B. Bar',
                 'F.B. Bar',
                 'F. Bar',
                 'Jean de Savigny',
                 'Jean la Tour',
                 'Jean le Tour',
                 'Mike ben Akar',
                 #'Jean de la Tour',
                 #'Johannes Diderik van der Waals',
                 ]

result = bibtexparser.customization.format_names(names)
print(result)

expected = ['Bar, Foo',
            'Bar, Foo B.',
            'Bar, F. B.',
            'Bar, F. B.',
            'Bar, F.',
            'de Savigny, Jean',
            'la Tour, Jean',
            'le Tour, Jean',
            'ben Akar, Mike',
            #'de la Tour, Jean',
            #'van der Waals, Johannes Diderik',
            ]
"""
