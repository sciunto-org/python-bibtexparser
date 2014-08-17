class BibDatabase(object):
    def __init__(self):
        self.entries = []
        self.entries_dict = {}
        self.comments = []
        self.strings = []
        self.preamble = []

    def get_entry_list(self):
        """Get a list of bibtex entries.

        :returns: list -- entries
        .. deprecated:: 0.5.6
           Use :attr:`entries` instead.
        """
        return self.entries

    def get_entry_dict(self):
        """Get a dictionnary of bibtex entries.
        The dict key is the bibtex entry key

        :returns: dict -- entries
        """
        # If the hash has never been made, make it
        if len(self.entries_dict) == 0:
            for entry in self.entries:
                self.entries_dict[entry['id']] = entry
        return self.entries_dict