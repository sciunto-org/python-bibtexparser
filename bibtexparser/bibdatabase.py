class BibDatabase(object):
    """
    A bibliographic database object following the data structure of a BibTeX file.
    """
    def __init__(self):
        #: List of BibTeX entries, for example `book`, `article`, etc. Each entry is a simple dict with BibTeX field-value
        #: pairs, for example `'author': 'Bird, R.B. and Armstrong, R.C. and Hassager, O.'`
        self.entries = []
        self._entries_dict = {}
        #: List of BibTex comment (`@comment{...}`) blocks.
        self.comments = []
        self.strings = []
        self.preamble = []

    def get_entry_list(self):
        """Get a list of bibtex entries.

        :returns: BibTeX entries
        :rtype: list
        .. deprecated:: 0.5.6
           Use :attr:`entries` instead.
        """
        return self.entries

    def get_entry_dict(self):
        """Return a dictionary of BibTeX entries.
        The dict key is the BibTeX entry key
        """
        # If the hash has never been made, make it
        if len(self._entries_dict) == 0:
            for entry in self.entries:
                self._entries_dict[entry['id']] = entry
        return self._entries_dict

    entries_dict = property(get_entry_dict)