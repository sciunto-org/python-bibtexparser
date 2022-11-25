import abc
from copy import copy
from typing import Any, Dict, List, Optional, Set


class Block(abc.ABC):
    def __init__(
        self,
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
        parser_metadata: Optional[Dict[str, Any]] = None,
    ):
        self._start_line_in_file = start_line
        self._raw = raw
        self._parser_metadata: Dict[str, Any] = parser_metadata
        if parser_metadata is None:
            self._parser_metadata: Dict[str, Any] = {}

    @property
    def start_line(self) -> Optional[int]:
        return self._start_line_in_file

    @property
    def raw(self) -> Optional[str]:
        return self._raw

    @property
    def parser_metadata(self) -> Dict[str, Any]:
        return self._parser_metadata

    def __eq__(self, other):
        # make sure they have the same type and same content
        return (
            isinstance(other, self.__class__)
            and isinstance(self, other.__class__)
            and self.__dict__ == other.__dict__
        )


class String(Block):
    """Bibtex Blocks of the `@string` type, e.g. @string{me = "My Name"}."""

    def __init__(
        self,
        key: str,
        value: str,
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
    ):
        super().__init__(start_line, raw)
        self._key = key
        self._value = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value


class Preamble(Block):
    """Bibtex Blocks of the `@preamble` type, e.g. @preamble{This is a preamble}."""

    def __init__(
        self, value: str, start_line: Optional[int] = None, raw: Optional[str] = None
    ):
        super().__init__(start_line, raw)
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value


class ExplicitComment(Block):
    """Bibtex Blocks of the `@comment` type, e.g. @comment{This is a comment}."""

    def __init__(
        self, comment: str, start_line: Optional[int] = None, raw: Optional[str] = None
    ):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value


class ImplicitComment(Block):
    """Bibtex outside of an @{...} block, which is treated as a comment."""

    def __init__(
        self, comment: str, start_line: Optional[int] = None, raw: Optional[str] = None
    ):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value


class Field:
    """A field of a Bibtex entry, e.g. `author = {John Doe}`."""

    def __init__(self, key: str, value: Any, start_line: Optional[int] = None):
        self._start_line = start_line
        self._key = key
        self._value = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any):
        self._value = value

    @property
    def start_line(self) -> int:
        return self._start_line

    def __eq__(self, other):
        # make sure they have the same type and same content
        return (
            isinstance(other, self.__class__)
            and isinstance(self, other.__class__)
            and self.__dict__ == other.__dict__
        )


class Entry(Block):
    """Bibtex Blocks of the `@entry` type, e.g. @article{Cesar2013, ...}."""

    def __init__(
        self,
        entry_type: str,
        key: str,
        fields: Dict[str, Field],
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
    ):
        super().__init__(start_line, raw)

        self._entry_type = entry_type
        self._key = key
        self._fields = fields
        self._parsing_metadata: Dict[str, Any] = {}

    @property
    def entry_type(self):
        return self._entry_type

    @entry_type.setter
    def entry_type(self, value: str):
        self._entry_type = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def fields(self) -> Dict[str, Field]:
        return copy(self._fields)

    @fields.setter
    def fields(self, value: Dict[str, Field]):
        self._fields = value

    def set_field(self, field: Field):
        """Adds a new field, or replaces existing with same key."""
        self._fields[field.key] = field

    def get_parser_metadata(self, key: str) -> Optional[Any]:
        return self._parsing_metadata.get(key, None)

    def set_parser_metadata(self, key: str, value: Any):
        self._parsing_metadata[key] = value

    def __getitem__(self, key: str) -> Any:
        """Dict-mimicking index, for partial v1.x backwards compatibility.

        For newly written code, it's recommended to use `entry.entry_type`,
        `entry.key` and `entry.fields[<<field-key>>].value` instead."""
        if key == "ENTRYTYPE":
            return self.entry_type
        if key == "ID":
            return self.key
        return self._fields[key].value

    def items(self):
        """Dict-mimicking, for partial v1.x backwards compatibility.

        For newly written code, it's recommended to use `entry.entry_type`,
        `entry.key` and `entry.fields` instead."""
        return [
            ("ENTRYTYPE", self.entry_type),
            ("ID", self.key),
        ] + [(f.key, f.value) for f in self.fields.values()]


class ParsingFailedBlock(Block):
    """A block that could not be parsed."""

    def __init__(
        self,
        error: Exception,
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
    ):
        super().__init__(start_line, raw)
        self._error = error

    @property
    def error(self) -> Exception:
        return self._error


class MiddlewareErrorBlock(ParsingFailedBlock):
    """A block that could not be parsed due to a middleware error."""

    def __init__(self, block: Block, error: Exception):
        super().__init__(start_line=block.start_line, raw=block.raw, error=error)
        self._block = block

    @property
    def block(self) -> Block:
        return self._block


class DuplicateEntryKeyBlock(ParsingFailedBlock):
    """A block that has a duplicate key."""

    def __init__(
        self,
        key: str,
        previous_block: Block,
        duplicate_block: Block,
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
    ):
        super().__init__(
            error=Exception(f"Duplicate entry key '{key}'"),
            start_line=start_line,
            raw=raw,
        )
        self._key = key
        self._previous_block = previous_block
        self._duplicate_block = duplicate_block

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def previous_block(self) -> Block:
        return self._previous_block

    @property
    def duplicate_block(self) -> Block:
        return self._duplicate_block


class DuplicateFieldKeyBlock(ParsingFailedBlock):
    def __init__(self, duplicate_keys: Set[str], entry: Entry):
        sorted_duplicate_keys = sorted(list(duplicate_keys))
        super().__init__(
            error=Exception(
                f"Duplicate field keys on entry: '{', '.join(sorted_duplicate_keys)}'."
                f"Note: The entry (containing duplicate) is available as `failed_block.entry`"
            ),
            start_line=entry.start_line,
            raw=entry.raw,
        )
        self._duplicate_keys: Set[str] = duplicate_keys
        self._entry: Entry = entry

    @property
    def duplicate_keys(self) -> Set[str]:
        return self._duplicate_keys

    @property
    def entry(self) -> Entry:
        return self._entry
