from copy import deepcopy
from typing import List, Optional, Union

from .library import Library
from .model import (
    Entry,
    ExplicitComment,
    Field,
    ImplicitComment,
    ParsingFailedBlock,
    Preamble,
    String,
)

VAL_SEP = " = "
PARSING_FAILED_COMMENT = "% WARNING Parsing failed for the following {n} lines."


def _treat_entry(block: Entry, bibtex_format) -> List[str]:
    res = ["@", block.entry_type, "{", block.key, ",\n"]
    field: Field
    for i, field in enumerate(block.fields):
        res.append(bibtex_format.indent)
        res.append(field.key)
        res.append(_val_intent_string(bibtex_format, field.key))
        res.append(VAL_SEP)
        res.append(field.value)
        if bibtex_format.trailing_comma or i < len(block.fields) - 1:
            res.append(",")
        res.append("\n")
    res.append("}\n")
    return res


def _val_intent_string(bibtex_format: "BibtexFormat", key: str) -> str:
    """The spaces which have to be added after the ` = `."""
    length = bibtex_format.value_column - len(key) - len(VAL_SEP)
    return "" if length <= 0 else " " * length


def _treat_string(block: String, bibtex_format) -> List[str]:
    return [
        "@string{",
        block.key,
        VAL_SEP,
        block.value,
        "}\n",
    ]


def _treat_preamble(block: Preamble, bibtex_format: "BibtexFormat") -> List[str]:
    return [f"@preamble{{{block.value}}}\n"]


def _treat_impl_comment(
    block: ImplicitComment, bibtex_format: "BibtexFormat"
) -> List[str]:
    # Note: No explicit escaping is done here - that should be done in middleware
    return [block.comment, "\n"]


def _treat_expl_comment(
    block: ExplicitComment, bibtex_format: "BibtexFormat"
) -> List[str]:
    return ["@comment{", block.comment, "}\n"]


def _treat_failed_block(
    block: ParsingFailedBlock, bibtex_format: "BibtexFormat"
) -> List[str]:
    lines = len(block.raw.splitlines())
    parsing_failed_comment = PARSING_FAILED_COMMENT.format(n=lines)
    return [parsing_failed_comment, "\n", block.raw, "\n"]


def _calculate_auto_value_align(library: Library) -> int:
    max_key_len = 0
    for entry in library.entries:
        for key in entry.fields_dict:
            max_key_len = max(max_key_len, len(key))
    return max_key_len + len(VAL_SEP)


def write(library: Library, bibtex_format: Optional["BibtexFormat"] = None) -> str:
    """Serialize a BibTeX database to a string.

    Note: This is not the exposed writing entrypoint.
    The exposed entrypoint is `bibtexparser.write_string` (in entrypoint.py).

    :param library: BibTeX database to serialize.
    :param bibtex_format: Customized BibTeX format to use (optional)."""
    if bibtex_format is None:
        bibtex_format = BibtexFormat()

    if bibtex_format.value_column == "auto":
        auto_val: int = _calculate_auto_value_align(library)
        # Copy the format instance to avoid modifying the original
        # (which would be bad if the format is used for multiple libraries)
        bibtex_format = deepcopy(bibtex_format)
        bibtex_format.value_column = auto_val

    string_pieces = []

    for i, block in enumerate(library.blocks):
        # Get string representation (as list of strings) of block
        string_block_pieces = _treat_block(bibtex_format, block)
        string_pieces.extend(string_block_pieces)
        # Separate Blocks
        if i < len(library.blocks) - 1:
            string_pieces.append(bibtex_format.block_separator)

    return "".join(string_pieces)


def _treat_block(bibtex_format, block) -> List[str]:
    if isinstance(block, Entry):
        string_block_pieces = _treat_entry(block, bibtex_format)
    elif isinstance(block, String):
        string_block_pieces = _treat_string(block, bibtex_format)
    elif isinstance(block, Preamble):
        string_block_pieces = _treat_preamble(block, bibtex_format)
    elif isinstance(block, ExplicitComment):
        string_block_pieces = _treat_expl_comment(block, bibtex_format)
    elif isinstance(block, ImplicitComment):
        string_block_pieces = _treat_impl_comment(block, bibtex_format)
    elif isinstance(block, ParsingFailedBlock):
        string_block_pieces = _treat_failed_block(block, bibtex_format)
    else:
        raise ValueError(f"Unknown block type: {type(block)}")
    return string_block_pieces


class BibtexFormat:
    """Definition of formatting (alignment, ...) when writing a BibTeX file.

    Hint: For more manual, GUI-based formatting, see the `bibtex-tidy` tool:
        https://flamingtempura.github.io/bibtex-tidy/
    """

    def __init__(self):
        self._indent: str = "\t"
        self._align_field_values: Union[int, str] = 0
        self._block_separator: str = "\n\n"
        self._trailing_comma: bool = False
        self._parsing_failed_comment: str = PARSING_FAILED_COMMENT

    @property
    def indent(self) -> str:
        """Character(s) for indenting BibTeX field-value pairs. Default: single space."""
        return self._indent

    @indent.setter
    def indent(self, indent: str):
        self._indent = indent

    @property
    def value_column(self) -> Union[int, str]:
        """Controls the alignment of field- and string-values. Default: no alignment.

        This impacts String and Entry blocks.

        An integer value x specifies that spaces should be added before the " = ",
        such that, if possible, the value is written at column `len(self.indent) + x`.
        Note that for long keys, the value may be written at a later column.

        Thus, a value of 0 means that the value is written directly after the " = ".

        The special value "auto" specifies that the bibtex field value should be aligned
        based on the longest key in the library.
        """
        return self._align_field_values

    @value_column.setter
    def value_column(self, align_values: Union[int, str]):
        if isinstance(align_values, int):
            if align_values < 0:
                raise ValueError("align_field_values must be >= 0")
        elif align_values != "auto":
            raise ValueError("align_field_values must be an integer or 'auto'")
        self._align_field_values = align_values

    @property
    def block_separator(self) -> str:
        """Character(s) for separating BibTeX entries.

        Default: Two lines breaks, i.e., two blank lines."""
        return self._block_separator

    @block_separator.setter
    def block_separator(self, entry_separator: str):
        self._block_separator = entry_separator

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

    @property
    def parsing_failed_comment(self) -> str:
        """Comment to use for blocks that could not be parsed."""
        return self._parsing_failed_comment

    @parsing_failed_comment.setter
    def parsing_failed_comment(self, parsing_failed_comment: str):
        self._parsing_failed_comment = parsing_failed_comment
