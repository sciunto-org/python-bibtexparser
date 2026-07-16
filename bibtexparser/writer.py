from copy import deepcopy
from typing import Optional

from .library import Library
from .model import Entry
from .model import ExplicitComment
from .model import Field
from .model import ImplicitComment
from .model import ParsingFailedBlock
from .model import Preamble
from .model import String

VAL_SEP = " = "
PARSING_FAILED_COMMENT = "% WARNING Parsing failed for the following {n} lines."
FAILED_BLOCK_POLICIES = ("preserve", "annotate", "raise")


def _treat_entry(block: Entry, bibtex_format) -> list[str]:
    res = ["@", block.entry_type, "{", block.key, ",\n"]
    field: Field
    for i, field in enumerate(block.fields):
        res.append(bibtex_format.indent)
        res.append(field.key)
        res.append(_val_indent_string(bibtex_format, field.key))
        res.append(VAL_SEP)
        res.append(field.value)
        if bibtex_format.trailing_comma or i < len(block.fields) - 1:
            res.append(",")
        res.append("\n")
    res.append("}\n")
    return res


def _val_indent_string(bibtex_format: "BibtexFormat", key: str) -> str:
    """The spaces which have to be added after the ` = `."""
    length = bibtex_format.value_column - len(key) - len(VAL_SEP)
    return "" if length <= 0 else " " * length


def _treat_string(block: String, bibtex_format) -> list[str]:
    return [
        "@string{",
        block.key,
        _val_indent_string(bibtex_format, block.key),
        VAL_SEP,
        block.value,
        "}\n",
    ]


def _treat_preamble(block: Preamble, bibtex_format: "BibtexFormat") -> list[str]:
    return [f"@preamble{{{block.value}}}\n"]


def _treat_impl_comment(block: ImplicitComment, bibtex_format: "BibtexFormat") -> list[str]:
    # Note: No explicit escaping is done here - that should be done in middleware
    return [block.comment, "\n"]


def _treat_expl_comment(block: ExplicitComment, bibtex_format: "BibtexFormat") -> list[str]:
    return ["@comment{", block.comment, "}\n"]


def _treat_failed_block(block: ParsingFailedBlock, bibtex_format: "BibtexFormat") -> list[str]:
    if block.raw is None:
        raise ValueError(_failed_blocks_without_raw_error([block]))
    if bibtex_format.failed_block_policy == "preserve":
        return [block.raw]
    if bibtex_format.failed_block_policy == "raise":
        # The complete-library check in `write` normally reports all failures at
        # once. Keep this guard so direct internal use cannot bypass the policy.
        raise ValueError(_failed_blocks_forbidden_error([block]))
    lines = len(block.raw.splitlines())
    parsing_failed_comment = bibtex_format.parsing_failed_comment.format(n=lines)
    return [parsing_failed_comment, "\n", block.raw, "\n"]


def _failed_blocks_without_raw_error(blocks: list[ParsingFailedBlock]) -> str:
    descriptions = "\n".join(f"  - {type(b).__name__}: {b.error}" for b in blocks)
    return (
        "Cannot write library: it contains failed blocks without raw bibtex "
        "(typically created programmatically, not by parsing):\n"
        f"{descriptions}\n"
        "Inspect `library.failed_blocks` to resolve this, e.g. by removing these blocks "
        "or by fixing and re-adding their `block.ignore_error_block`."
    )


def _failed_blocks_forbidden_error(blocks: list[ParsingFailedBlock]) -> str:
    descriptions = "\n".join(f"  - {type(b).__name__}: {b.error}" for b in blocks)
    return (
        "Cannot write library with failed_block_policy='raise':\n"
        f"{descriptions}\n"
        "Inspect `library.failed_blocks` and resolve or remove every failed block, "
        "or select the 'preserve' or 'annotate' policy explicitly."
    )


def _raise_on_unwritable_blocks(library: Library) -> None:
    unwritable = [b for b in library.blocks if isinstance(b, ParsingFailedBlock) and b.raw is None]
    if unwritable:
        raise ValueError(_failed_blocks_without_raw_error(unwritable))


def _raise_when_failed_blocks_are_forbidden(
    library: Library, bibtex_format: "BibtexFormat"
) -> None:
    if bibtex_format.failed_block_policy != "raise":
        return
    failed_blocks = [b for b in library.blocks if isinstance(b, ParsingFailedBlock)]
    if failed_blocks:
        raise ValueError(_failed_blocks_forbidden_error(failed_blocks))


def _calculate_auto_value_align(library: Library) -> int:
    max_key_len = 0
    for entry in library.entries:
        for key in entry.fields_dict:
            max_key_len = max(max_key_len, len(key))
    for string in library.strings:
        max_key_len = max(max_key_len, len(string.key))
    return max_key_len + len(VAL_SEP)


def write(library: Library, bibtex_format: Optional["BibtexFormat"] = None) -> str:
    """Serialize a BibTeX database to a string.

    Note: This is not the exposed writing entrypoint.
    The exposed entrypoint is `bibtexparser.write_string` (in entrypoint.py).

    :param library: BibTeX database to serialize.
    :param bibtex_format: Customized BibTeX format to use (optional).
    :raises ValueError: If the library contains failed blocks without raw bibtex
        (e.g. duplicate-key blocks resulting from programmatically created entries)."""
    if bibtex_format is None:
        bibtex_format = BibtexFormat()

    _raise_on_unwritable_blocks(library)
    _raise_when_failed_blocks_are_forbidden(library, bibtex_format)

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


def _treat_block(bibtex_format, block) -> list[str]:
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
        self._align_field_values: int | str = 0
        self._block_separator: str = "\n\n"
        self._trailing_comma: bool = False
        self._parsing_failed_comment: str = PARSING_FAILED_COMMENT
        self._failed_block_policy: str = "preserve"

    @property
    def indent(self) -> str:
        """Character(s) for indenting BibTeX field-value pairs. Default: single tab."""
        return self._indent

    @indent.setter
    def indent(self, indent: str):
        self._indent = indent

    @property
    def value_column(self) -> int | str:
        """Controls the alignment of field- and string-values. Default: no alignment.

        This impacts String and Entry blocks.

        An integer value x specifies that spaces should be added before the " = ",
        such that, if possible, the value starts x characters after the line prefix
        (the ``indent`` for entry fields, ``@string{`` for string values).
        Entry and string values are thus each aligned among themselves.
        Note that for long keys, the value may be written at a later column.

        Thus, a value of 0 means that the value is written directly after the " = ".

        The special value "auto" specifies that values should be aligned
        based on the longest key in the library
        (considering both entry field keys and string keys).
        """
        return self._align_field_values

    @value_column.setter
    def value_column(self, align_values: int | str):
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

    @property
    def failed_block_policy(self) -> str:
        """Control writing of blocks that could not be parsed.

        ``"preserve"`` (the default) writes the retained raw block without
        modifying it. This makes repeated parse/write cycles stable and avoids
        accumulating generated warning comments.

        ``"annotate"`` prepends ``parsing_failed_comment`` to the raw block.
        This is the behavior used before the policy was introduced, but it
        intentionally changes the document on every parse/write cycle.

        ``"raise"`` refuses to write a library containing any failed block.
        Use it when every parse failure must be resolved before export.
        """
        return self._failed_block_policy

    @failed_block_policy.setter
    def failed_block_policy(self, failed_block_policy: str):
        if failed_block_policy not in FAILED_BLOCK_POLICIES:
            choices = ", ".join(repr(policy) for policy in FAILED_BLOCK_POLICIES)
            raise ValueError(f"failed_block_policy must be one of {choices}")
        self._failed_block_policy = failed_block_policy
