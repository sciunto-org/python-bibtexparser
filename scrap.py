
from compare_names import *

file = 'bibtexparser/tests/data/random.bib'

cleaner = AuthorOrganizer(file)

cleaner.clean_authors()
