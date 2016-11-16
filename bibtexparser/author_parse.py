#!/usr/bin/env python3


"""
This script merges a new bib file with an existing one.

It is not very smart -- mostly what it does is give a "Chris Style" key.

Then , with the merge it will make sure you don't have duplicate keys --
but it will allow duplicate entries!

We can make that smarter, later, but duplicates can be hard to identify!


The "hard" part of this script is parsing the author string -- that's tricky!

Using info from:

http://nwalsh.com/tex/texhelp/bibtx-23.html

and

"The LaTeX companion"

To figure out bibTeX author parsing

The tests include all the examples in The LaTeX Companion (1993)

NOTE: This would probably be more robust if it were re-written to do the tokenizing
      directly in a TeX aware way i.e. handling {} and \commands{} exactly like TeX does.
      But then it couldn't use python's nifty built-in string methods.
"""

import bibtexparser

new_filename = "endnote_export.bib"
main_filename = "gnome_references.bib"


class Author():
    """
    Holds a Author object -- really just a few fields

    Also contains code for parsing BiBTeX author strings
    """
    # using Unicode "Private use areas"
    # these are used to replace spaces and commas inside {}
    # so everyting within a bracket will be treated as one token
    replace_space = "\uE000"  # "_"
    replace_comma = "\uE001"  # "`"
    replace_and = "\uE001"

    def __init__(self, first='', von='', last='', jr=''):
        self.first = first.strip()
        self.von = von.strip()
        self.last = last.strip()
        self.jr = jr.strip()

    def split_authors(self, author_str):
        """
        parses the complete author string to break up multiple authors

        returns a list of authors: each author is a string
        """
        print(author_str)

        # splitting on "and", but bracket aware:
        brackets = 0
        and_ind = []
        for i, c in enumerate(author_str[:]):
            if c == "{":
                brackets += 1
            elif c == "}":
                brackets -= 1
            elif not brackets:
                if author_str[i:i + 3] == "and":
                    and_ind.append(i)
        print("and indexes:", and_ind)
        authors = []
        for i in and_ind:
            print (author_str)
            authors.append(author_str[:i].strip())
            author_str = author_str[i + 3:]
            print(authors, author_str)
        authors.append(author_str.strip())
        print(authors)

        return authors

    @staticmethod
    def firstislower(s):
        """
        an islower() function that finds if th first letter is lower case,
        ignoring TeX control sequences

        used to find "von" parts of names
        """
        ind = 0
        in_control = False
        for c in s:
            if c == "{":
                ind += 1
                in_control = False
            elif c == "\\":
                ind += 1
                in_control = True
            else:
                if not in_control:
                    return c.islower()
        return False

    @classmethod
    def from_string(cls, string):
        # raw string -- there is a \u in there!
        r"""
        create an author object from a BiBTex compatible string

        Apparently there are three options for names:

        "First von Last" "von Last, First" "von Last, Jr, First"

        So I use the number of commas to figure out which this is

        fixme: this doesn't handle {} correctly -- {} can be used
               to group extra stuff an commas into one part of a name.

               it also won't handle capitalization of von:
               Maria {\uppercase{d}e La} Cruz
               (the von should be "De La")

        """
        author = cls()  # so we can use instance methods
        string = author.pre_processs_brackets(string)

        first, von, last, jr = ('',) * 4
        string = string.strip()
        # if there is a comma, the first name is after the comma
        if "," in string:
            parts = string.rsplit(",", 1)
            first = parts[1].strip()
            string = parts[0].strip()

            # now if there is still a comma, it's a Jr
            print("first name removed:", first, repr(string))
            parts = string.partition(",")
            jr = parts[2]
            string = parts[0]
            print("Jr removed:", jr, repr(string))

        # # take off the last name
        # try:
        #     string, last = string.rsplit(maxsplit=1)
        # except ValueError:
        #     string, last = "", string

        # now look for the von:
        #  which can be before a double last name -- arrgg!
        if string:
            print("splitting on the von")
            parts = string.split()
            print(parts)
            # look for the von parts:
            if len(parts) == 1:  # only one token, must be the last name
                last = parts[0]
            else:
                von1, von2 = -1, 0
                for i, part in enumerate(parts):
                    if author.firstislower(part):  # It's a von
                        print("found a von:", part, von1, von2)
                        von2 = i + 1
                        von1 = i if von1 == -1 else von1
                        print(von1, von2)
                print("von indexes:", von1, von2)
                if von1 > -1:
                    von = " ".join(parts[von1:von2])
                    if not first:
                        first = " ".join(parts[:von1])
                    last = " ".join(parts[von2:])
                else:
                    if first:
                        last = " ".join(parts)
                    else:
                        last = parts[-1]
                        first = " ".join(parts[:-1])

        print("last name:", last)
        first, von, last, jr = [author.post_process_brackets(s) for s in (first, von, last, jr)]
        author.__init__(first, von, last, jr)
        return author

    def pre_processs_brackets(self, in_str, replace_and=False):
        """
        Replace whitespace and commas that are in brackets

        So that they won't be used for splitting, etc.

        fixme: It would probably be cleaner to write custom tokenizing code that
               respects brackets, rather than this kludge - but this was easy
        """
        # make sure any whitespace is a single regular space charactor:
        in_str = " ".join(in_str.split())
        out = []
        brackets = 0
        for c in in_str:
            if c == "{":
                brackets += 1
            elif c == "}":
                brackets -= 1
            if brackets:
                if c == " ":
                    out.append(self.replace_space)
                elif c == ",":
                    out.append(self.replace_comma)
                else:
                    out.append(c)
            else:
                out.append(c)
        return "".join(out)

    def post_process_brackets(self, in_str):
        """
        return the spaces and commas inside the brackets
        """
        return in_str.replace(self.replace_space, " ").replace(self.replace_comma, ",")

    def __eq__(self, other):
        """
        nice to have a way to check that Auther instances are the same

        for tests, if nothing else
        """
        try:
            if (self.first == other.first and
                self.von == other.von and
                self.last == other.last and
                self.jr == other.jr
                ):
                return True
            else:
                return False
        except AttributeError:  # other is not a duck-typed Author instance
            return False


if __name__ == "__main__":

    main()
