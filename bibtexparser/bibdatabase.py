from collections import OrderedDict
import sys


if sys.version_info.major == 2:
    TEXT_TYPE = unicode
else:
    TEXT_TYPE = str


class BibDatabase(object):
    """
    A bibliographic database object following the data structure of a BibTeX file.
    """
    def __init__(self):
        #: List of BibTeX entries, for example `@book{...}`, `@article{...}`, etc. Each entry is a simple dict with
        #: BibTeX field-value pairs, for example `'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'` Each
        #: entry will always have the following dict keys (in addition to other BibTeX fields):
        #:  - `ID` (BibTeX key)
        #:  - `ENTRYTYPE` (entry type in lowercase, e.g. `book`, `article` etc.)
        self.entries = []
        self._entries_dict = {}
        #: List of BibTeX comment (`@comment{...}`) blocks.
        self.comments = []
        #: OrderedDict of BibTeX string definitions (`@string{...}`). In order of definition.
        self.strings = OrderedDict()  # Not sure if order is import, keep order just in case
        #: List of BibTeX preamble (`@preamble{...}`) blocks.
        self.preambles = []

    def get_entry_list(self):
        """Get a list of bibtex entries.

        :returns: BibTeX entries
        :rtype: list
        .. deprecated:: 0.5.6
           Use :attr:`entries` instead.
        """
        return self.entries

    @staticmethod
    def entry_sort_key(entry, fields):
        result = []
        for field in fields:
            result.append(TEXT_TYPE(entry.get(field, '')).lower())  # Sorting always as string
        return tuple(result)

    def get_entry_dict(self):
        """Return a dictionary of BibTeX entries.
        The dict key is the BibTeX entry key
        """
        # If the hash has never been made, make it
        if not self._entries_dict:
            for entry in self.entries:
                self._entries_dict[entry['ID']] = entry
        return self._entries_dict

    entries_dict = property(get_entry_dict)
