import re
import sys
import fileinput

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

def levenshtein(s1, s2):
    """
    Levenshtein algorithm for detetermining string distance

    :param s1: string 1
    :param s2: string 2
    :return: Levenshtein distance between both strings
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def replace_all(file, search, replace):
    for line in fileinput.input(file, inplace=1):
        if search in line:
            line = line.replace(search, replace)
        sys.stdout.write(line)

class AuthorOrganizer(object):
    """
    Organizes the authors in a BibTex file. The self.clean_authors function checks a file
    for author names that may look similar for the following reasons:
    - absent/different accents
    - absent/different special characters
    - different use of capital letters
    - different use of brackets
    - initials seem to abbreviate a full name that is also present
    - typing errors

    Suggests to replace author names within the bibliographic file in command line.

    Example:

        file = 'bibfile.bib'

        cleaner = AuthorOrganizer(file)

        cleaner.clean_authors()
    """

    def __init__(self, file):
        self.file = file

    def similar_authors(self, author1, author2):
        """

        :param author1: dict
        :param author2: dict
        :return:
        """

        menu_1 = '\nAre%s %s and%s %s the same author?\n' \
                 '\nPlease insert the number corresponding to your answer:' \
                 '\n1. Yes \n2. No\n' \
                 % (author1["original_first"], author1["original_last"],
                    author2["original_first"], author2["original_last"])

        menu_2 = '\nPlease choose one of the actions below by inserting the corresponding number:' \
                 '\n1. Ignore\n2. Replace occurrences of %s %s by %s %s.\n' \
                 '3. Replace occurrences of %s %s by %s %s.\n' % \
                 (author1["original_first"], author1["original_last"],
                    author2["original_first"], author2["original_last"],
                    author2["original_first"], author2["original_last"],
                    author1["original_first"], author1["original_last"])

        answer = input(menu_1)

        while (not answer in ['1','2']):
            print('Invalid answer.')
            answer = input(menu_1)

        if answer == '1':
            action = input(menu_2)
            while (not action in ['1', '2', '3']):
                print('Invalid answer.')
                action = input(menu_2)
            if action != '1':
                file = self.file

                name1_first = author1["original_first"].strip() + ' ' + author1["original_last"].strip()
                name2_first = author2["original_first"].strip() + ' ' + author2["original_last"].strip()
                name1_last = author1["original_last"].strip() + ', ' + author1["original_first"].strip()
                name2_last = author2["original_last"].strip() + ', ' + author2["original_first"].strip()

                if action == '2':
                    replace_all(file, name1_first, name2_first)
                    replace_all(file, name1_last, name2_last)
                if action == '3':
                    replace_all(file, name2_first, name1_first)
                    replace_all(file, name2_last, name1_last)

    def clean_authors(self):
        with open(self.file, 'r') as bibtex_file:
            parser = BibTexParser()
            bib_database = bibtexparser.load(bibtex_file, parser=parser)

        authors = []
        weird_characters = ['\\', '\'', '{', '}', '"']

        for entry in bib_database.entries:

            if "author" in entry:
                if isinstance(entry["author"], list):
                    authors_entry = entry["author"]
                else:
                    authors_entry = getnames([i.strip() for i in entry["author"].replace('\n', ' ').split(" and ")])

            for author in authors_entry:

                author_split = author.split(',', 1)
                author_dict = dict()
                author_dict["original_last"] = author_split[0]
                author_dict["original_first"] = author_split[1]

                new_entry = 0
                for dictionary in authors:
                    if (dictionary["original_last"] == author_dict["original_last"]) and (dictionary["original_first"] == author_dict["original_first"]):
                        new_entry += 1

                if new_entry == 0:
                    # remove special characters from names
                    author = re.sub('\\\\v', '', author)
                    for item in weird_characters:
                        author = author.replace(item, '')
                    author_split = author.split(',', 1)

                    author_dict["last"] = author_split[0]
                    author_dict["first"] = author_split[1]
                    if '.' in author_dict["first"]:
                        author_dict["initials"] = True
                    else:
                        author_dict["initials"] = False

                    if (author_dict["original_first"] != author_dict["first"]) or (author_dict["original_last"] != author_dict["last"]):
                        author_dict["changed"] = True
                    else:
                        author_dict["changed"] = False

                    authors.append(author_dict)

        authors_updated = authors
        for author1 in authors:
            authors_updated = [x for x in authors_updated if x != author1]
            for author2 in authors_updated:

                # identical last names, one changed
                if (levenshtein(author1["last"], author2["last"]) == 0) and ((author1["changed"] == True) or (author2["changed"] == True)):
                    if (author1["initials"] == False) and (author2["initials"] == False):
                        if 0 <= levenshtein(author1["first"], author2["first"]) <= 2:
                            self.similar_authors(author1, author2)
                    if (author1["initials"] == True) and (author2["initials"] == True):
                        if 0 <= levenshtein(author1["first"], author2["first"]) <= 2:
                            self.similar_authors(author1, author2)

                # similar last names
                elif 0 < levenshtein(author1["last"], author2["last"]) <= 2:
                    if (author1["initials"] == False) and (author2["initials"] == False):
                            if 0 <= levenshtein(author1["first"], author2["first"]) <= 2:
                                self.similar_authors(author1, author2)
                    if (author1["initials"] == True) and (author2["initials"] == True):
                            if 0 <= levenshtein(author1["first"], author2["first"]) <= 2:
                                self.similar_authors(author1, author2)

                # similar first names/initials
                elif (author1["initials"] == author2["initials"]):
                    if (levenshtein(author1["first"], author2["first"]) == 0) and ((author1["changed"] == True) or (author2["changed"] == True)):
                        if 0 <= levenshtein(author1["last"], author2["last"]) <= 2:
                            self.similar_authors(author1, author2)
                    if 0 < levenshtein(author1["first"], author2["first"]) <= 2:
                        if 0 <= levenshtein(author1["last"], author2["last"]) <= 2:
                            self.similar_authors(author1, author2)

                # initials may correspond to names
                elif (author1["initials"] == True) and (author2["initials"] == False):
                    initials1 = author1["first"].replace(' ', '')
                    initials2 = ''
                    for name in author2["first"].split():
                        initials2 += name[0] + '.'
                    if (initials1 == initials2) and (0 <= levenshtein(author1["last"], author2["last"]) <= 2):
                        self.similar_authors(author1, author2)

                elif (author1["initials"] == False) and (author2["initials"] == True):
                    initials2 = author2["first"].replace(' ', '')
                    initials1 = ''
                    for name in author1["first"].split():
                        initials1 += name[0] + '.'
                    if (initials1 == initials2) and (0 <= levenshtein(author1["last"], author2["last"]) <= 2):
                        self.similar_authors(author1, author2)

    # TODO: implement all changes in one single execution
    def clean(self):
        self.clean_authors()
        self.clean_authors()
