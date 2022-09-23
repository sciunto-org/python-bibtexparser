import abc
from typing import Any, Dict, List, Optional

# TODO Overwrite copy and deepcopy dundermethods


class Block(abc.ABC):
    def __init__(self, start_line: int, raw: str):
        self._start_line_in_file = start_line
        self._raw = raw

    @property
    def start_line(self) -> int:
        return self._start_line_in_file

    @property
    def raw(self) -> str:
        return self._raw


class String(Block):
    """Bibtex Blocks of the `@string` type, e.g. @string{me = "My Name"}."""

    def __init__(self, start_line: int, raw: str, key: str, value: str):
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

    def __init__(self, start_line: int, raw: str, value: str):
        super().__init__(start_line, raw)
        self._value = value

    @property
    def value(self) -> str:
        return self._value


class ExplicitComment(Block):
    """Bibtex Blocks of the `@comment` type, e.g. @comment{This is a comment}."""

    def __init__(self, start_line: int, raw: str, comment: str):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        return self._comment


class ImplicitComment(Block):
    """Bibtex outside of an @{...} block, which is treated as a comment."""

    def __init__(self, start_line: int, raw: str, comment: str):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        return self._comment


class Field:
    """A field of a Bibtex entry, e.g. `author = {John Doe}`."""

    def __init__(self, start_line: int, key: str, value: str):
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
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value


class Entry(Block):
    """Bibtex Blocks of the `@entry` type, e.g. @article{Cesar2013, ...}."""

    def __init__(
        self,
        start_line: int,
        raw: str,
        entry_type: str,
        key: str,
        fields: Dict[str, Field],
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
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value: List[Field]):
        self._fields = value

    def get_parser_metadata(self, key: str) -> Optional[Any]:
        return self._parsing_metadata.get(key, None)

    def set_parser_metadata(self, key: str, value: Any):
        self._parsing_metadata[key] = value


class ParsingFailedBlock(Block):
    """A block that could not be parsed."""

    def __init__(self, start_line: int, raw: str, error: Exception):
        super().__init__(start_line, raw)
        self._error = error

    @property
    def error(self) -> Exception:
        return self._error


class DuplicateKeyBlock(Block):
    """A block that has a duplicate key."""

    def __init__(
        self,
        start_line: int,
        raw: str,
        key: str,
        previous_block: Block,
        duplicate_block: Block,
    ):
        super().__init__(start_line, raw)
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
