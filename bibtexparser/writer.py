from typing import Optional

from bibtexparser.library import Library


def write_string(
    library: Library, bibtex_format: Optional["BibtexFormat"] = None
) -> str:
    """Serialize a BibTeX database to a string.

    Note: This is not the exposed writing entrypoint.
    The exposed entrypoint is `bibtexparser.write_string` (in entrypoint.py).

    :param library: BibTeX database to serialize.
    :param bibtex_format: Customized BibTeX format to use (optional)."""
    if bibtex_format is None:
        bibtex_format = BibtexFormat()

    # TODO implement conversion from bib_database to bibtex string
    #    This is probably requiring many helper methods
    #    and we thus *may* have to change the structure of the file a bit
    #    (e.g. using a static methods on a class)

    raise NotImplementedError("Bibtex string writing not yet implemented")


class BibtexFormat:
    """Definition of formatting (alignment, ...) when writing a BibTeX file.

    Hint: For more manual, GUI-based formatting, see the `bibtex-tidy` tool:
        https://flamingtempura.github.io/bibtex-tidy/
    """

    def __init__(self):
        self._indent: str = " "
        self._align_values: bool = False
        self._align_multiline_values: bool = False
        self._entry_separator: str = "\n"
        self._comma_first: bool = False
        self._trailing_comma: bool = False

    @property
    def indent(self) -> str:
        """Character(s) for indenting BibTeX field-value pairs. Default: single space."""
        return self._indent

    @indent.setter
    def indent(self, indent: str):
        self._indent = indent

    @property
    def align_values(self) -> bool:
        """Specifies whether values should be aligned. Default: False

        If `true`, the maximal number of characters used in any fieldname
        is determined and all values are aligned according to that"""
        return self._align_values

    @align_values.setter
    def align_values(self, align_values: bool):
        self._align_values = align_values

    @property
    def align_multiline_values(self) -> bool:
        """Specifies whether multi-line values should be aligned. Default: False

        If `true`, multi-line values are formatted such that multiline text is
         aligned exactly on top of each other."""
        return self._align_multiline_values

    @align_multiline_values.setter
    def align_multiline_values(self, align_multiline_values: bool):
        self._align_multiline_values = align_multiline_values

    @property
    def entry_separator(self) -> str:
        """Character(s) for separating BibTeX entries. Default: single new line."""
        return self._entry_separator

    @entry_separator.setter
    def entry_separator(self, entry_separator: str):
        self._entry_separator = entry_separator

    @property
    def comma_first(self) -> bool:
        """Use the comma-first syntax for BibTeX entries. Default: False

        BibTeX syntax allows comma first syntax,
        which is common in functional languages.
        """
        return self._comma_first

    @comma_first.setter
    def comma_first(self, comma_first: bool):
        self._comma_first = comma_first

    @property
    def trailing_comma(self) -> bool:
        """Use the trailing comma syntax for BibTeX entries. Default: False

        BibTeX syntax allows an optional comma at the end
        of the last field in an entry.
        """
        return self._trailing_comma

    @trailing_comma.setter
    def trailing_comma(self, trailing_comma: bool):
        self._trailing_comma = trailing_comma
