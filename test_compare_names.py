from bibtexparser.compare_names import *

file = 'bibtexparser/tests/data/confusable_names.bib'

cleaner = AuthorOrganizer(file)
cleaner.take_longest_option = True

cleaner.clean_authors()