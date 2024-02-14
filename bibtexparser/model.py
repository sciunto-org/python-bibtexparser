import abc
from typing import Any, Dict, List, Optional, Set


class Block(abc.ABC):
    """A abstract superclass of all top-level building blocks of a bibtex file.

    E.g. a ``@string`` block, a ``@preamble`` block, an ``@entry`` block, a comment, etc.
    """

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
        """The line number of the first line of this block in the parsed string."""
        return self._start_line_in_file

    @property
    def raw(self) -> Optional[str]:
        """The raw, unmodified string (bibtex) representation of this block.

        Note: Middleware does not update this field, hence, after applying middleware
        to a library, this field may be outdated.
        """
        return self._raw

    @property
    def parser_metadata(self) -> Dict[str, Any]:
        """EXPERIMENTAL: field for middleware to store auxiliary information.

        As an end-user, as long as you are not writing middleware, you probably
        do not need to use this field.

        ** Warning (experimental) **
        The content of this field is undefined and may change at any time.

        This field is intended for middleware to store auxiliary information.
        It is a key-value store, where the key is a string and the value is any
        python object.
        This allows for example to pass information between different middleware.
        """
        return self._parser_metadata

    def get_parser_metadata(self, key: str) -> Optional[Any]:
        """EXPERIMENTAL: get auxiliary information stored in ``parser_metadata``.

        See attribute ``parser_metadata`` for more information."""
        return self._parser_metadata.get(key, None)

    def set_parser_metadata(self, key: str, value: Any):
        """EXPERIMENTAL: set auxiliary information stored in ``parser_metadata``.

        See attribute ``parser_metadata`` for more information."""
        self._parser_metadata[key] = value

    def __eq__(self, other):
        # make sure they have the same type and same content
        return (
            isinstance(other, self.__class__)
            and isinstance(self, other.__class__)
            and self.__dict__ == other.__dict__
        )


class String(Block):
    """Bibtex Blocks of the ``@string`` type, e.g. ``@string{me = "My Name"}``."""

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
        """The key of the string, e.g. ``me`` in ``@string{me = "My Name"}``."""
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def value(self) -> str:
        """The value of the string, e.g. ``"My Name"`` in ``@string{me = "My Name"}``."""
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    def __str__(self):
        return f"String (line: {self.start_line}, key: `{self.key}`): `{self.value}`"

    def __repr__(self):
        return (
            f"String(key=`{self.key}`, value=`{self.value}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class Preamble(Block):
    """Bibtex Blocks of the ``@preamble`` type, e.g. ``@preamble{This is a preamble}``."""

    def __init__(
        self, value: str, start_line: Optional[int] = None, raw: Optional[str] = None
    ):
        super().__init__(start_line, raw)
        self._value = value

    @property
    def value(self) -> str:
        """The value of the preamble, e.g. ``blabla`` in ``@preamble{blabla}``."""
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    def __str__(self):
        return f"Preamble (line: {self.start_line}): `{self.value}`"

    def __repr__(self):
        return (
            f"Preamble(value=`{self.value}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class ExplicitComment(Block):
    """Bibtex Blocks of the ``@comment`` type, e.g. ``@comment{This is a comment}``."""

    def __init__(
        self, comment: str, start_line: Optional[int] = None, raw: Optional[str] = None
    ):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        """The value of the comment, e.g. ``blabla`` in ``@comment{blabla}``."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def __str__(self):
        return f"ExplicitComment (line: {self.start_line}): `{self.comment}`"

    def __repr__(self):
        return (
            f"ExplicitComment(comment=`{self.comment}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class ImplicitComment(Block):
    """Bibtex outside of an ``@{...}`` block, which is treated as a comment."""

    def __init__(
        self, comment: str, start_line: Optional[int] = None, raw: Optional[str] = None
    ):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        """The (possibly multi-line) comment."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def __str__(self):
        return f"ImplicitComment (line: {self.start_line}): `{self.comment}`"

    def __repr__(self):
        return (
            f"ImplicitComment(comment=`{self.comment}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class Field:
    """A field of a Bibtex entry, e.g. ``author = {John Doe}``."""

    def __init__(self, key: str, value: Any, start_line: Optional[int] = None):
        self._start_line = start_line
        self._key = key
        self._value = value

    @property
    def key(self) -> str:
        """The key of the field, e.g. ``author`` in ``author = {John Doe}``."""
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def value(self) -> Any:
        """The value of the field, e.g. ``{John Doe}`` in ``author = {John Doe}``."""
        return self._value

    @value.setter
    def value(self, value: Any):
        self._value = value

    @property
    def start_line(self) -> int:
        """The line number of the first line of this field in the originally parsed string."""
        return self._start_line

    def __eq__(self, other):
        # make sure they have the same type and same content
        return (
            isinstance(other, self.__class__)
            and isinstance(self, other.__class__)
            and self.__dict__ == other.__dict__
        )

    def __str__(self):
        return f"Field (line: {self.start_line}, key: `{self.key}`): `{self.value}`"

    def __repr__(self):
        return (
            f"Field(key=`{self.key}`, value=`{self.value}`, "
            f"start_line={self.start_line})"
        )


class Entry(Block):
    """Bibtex Blocks of the ``@entry`` type, e.g. ``@article{Cesar2013, ...}``."""

    def __init__(
        self,
        entry_type: str,
        key: str,
        fields: List[Field],
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
    ):
        super().__init__(start_line, raw)
        self._entry_type = entry_type
        self._key = key
        self._fields = fields

    @property
    def entry_type(self):
        """The type of the entry, e.g. ``article`` in ``@article{Cesar2013, ...}``."""
        return self._entry_type

    @entry_type.setter
    def entry_type(self, value: str):
        self._entry_type = value

    @property
    def key(self):
        """The key of the entry, e.g. ``Cesar2013`` in ``@article{Cesar2013, ...}``."""
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def fields(self) -> List[Field]:
        """The key-value attributes of an entry, as ``Field`` instances."""
        return self._fields

    @fields.setter
    def fields(self, value: List[Field]):
        self._fields = value

    @property
    def fields_dict(self) -> Dict[str, Field]:
        """A dict of fields, with field keys as keys.

        Note that with duplicate field keys, the behavior is undefined."""
        return {field.key: field for field in self._fields}

    def set_field(self, field: Field):
        """Adds a new field, or replaces existing with same key."""
        if field.key in self.fields_dict:
            i = [f.key for f in self._fields].index(field.key)
            self._fields[i] = field
        else:
            self._fields.append(field)

    def pop(self, key: str, default=None) -> Optional[Field]:
        """Removes and returns the field with the given key.

        :param key: The key of the field to remove.
        :param default: The value to return if the field does not exist."""
        try:
            field = self.fields_dict.pop(key)
        except KeyError:
            return default

        self._fields = [f for f in self._fields if f.key != key]
        return field

    def get(self, key: str, default=None) -> Optional[Field]:
        """Returns the field with the given key, or the default value if it does not exist.

        :param key: The key of the field.
        :param default: The value to return if the field does not exist."""
        return self.fields_dict.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Dict-mimicking ``in`` operator."""
        return key in self.fields_dict

    def __getitem__(self, key: str) -> Any:
        """Dict-mimicking index.

        This serves for partial v1.x backwards compatibility,
        as well as for a shorthand for accessing field values.

        Note that with duplicate field keys, the behavior is undefined.
        """
        if key == "ENTRYTYPE":
            return self.entry_type
        if key == "ID":
            return self.key
        return self.fields_dict[key].value

    def __setitem__(self, key: str, value: Any):
        """Dict-mimicking index.

        This serves for partial v1.x backwards compatibility,
        as well as for a shorthand for `set_field`.
        """
        self.set_field(Field(key, value))

    def __delitem__(self, key):
        """Dict-mimicking index.

        This serves for partial v1.x backwards compatibility,
        as well as for a shorthand for `pop`.
        """
        self.pop(key)

    def items(self):
        """Dict-mimicking, for partial v1.x backwards compatibility.

        For newly written code, it's recommended to use `entry.entry_type`,
        `entry.key` and `entry.fields` instead."""
        return [
            ("ENTRYTYPE", self.entry_type),
            ("ID", self.key),
        ] + [(f.key, f.value) for f in self.fields]

    def __str__(self):
        lines = [
            f"Entry (line: {self.start_line}, type: `{self.entry_type}`, key: `{self.key}`):"
        ]
        lines.extend([f"\t`{f.key}` = `{f.value}`" for f in self.fields])
        return "\n".join(lines)

    def __repr__(self):
        return (
            f"Entry(entry_type=`{self.entry_type}`, key=`{self.key}`, "
            f"fields=`{self.fields.__repr__()}`, start_line={self.start_line})"
        )


class ParsingFailedBlock(Block):
    """A block that could not be parsed due to some raised exception."""

    def __init__(
        self,
        error: Exception,
        start_line: Optional[int] = None,
        raw: Optional[str] = None,
        ignore_error_block: Optional[Block] = None,
    ):
        super().__init__(start_line, raw)
        self._error = error
        self._ignore_error_block = ignore_error_block

    @property
    def error(self) -> Exception:
        """The exception that was raised during parsing."""
        return self._error

    @property
    def ignore_error_block(self) -> Optional[Block]:
        """The possibly faulty block when ignoring the error.

        This may be None, as it may not always be possible to ignore the error.
        For errors caused by middleware, this is typically the block without
        the middleware applied."""
        return self._ignore_error_block


class MiddlewareErrorBlock(ParsingFailedBlock):
    """A block that could not be parsed due to a middleware error.

    To get the block that caused this error, call `block.ignore_error_block`
    (which is the block with the middleware not or only partially applied)."""

    def __init__(self, block: Block, error: Exception):
        super().__init__(
            start_line=block.start_line,
            raw=block.raw,
            error=error,
            ignore_error_block=block,
        )


class DuplicateBlockKeyBlock(ParsingFailedBlock):
    """An error-indicating block created for blocks with keys present in the library already.

    To get the block that caused this error, call `block.ignore_error_block`."""

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
            ignore_error_block=duplicate_block,
        )
        self._key = key
        self._previous_block = previous_block

    @property
    def key(self) -> str:
        """The key of the entry, e.g. ``Cesar2013`` in ``@article{Cesar2013, ...}``."""
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def previous_block(self) -> Block:
        """A reference to a previous block with the same key."""
        return self._previous_block


class DuplicateFieldKeyBlock(ParsingFailedBlock):
    """An error-indicating block indicating a duplicate field key in an entry."""

    def __init__(self, duplicate_keys: Set[str], entry: Entry):
        sorted_duplicate_keys = sorted(list(duplicate_keys))
        super().__init__(
            error=Exception(
                f"Duplicate field keys on entry: '{', '.join(sorted_duplicate_keys)}'."
                f"Note: The entry (containing duplicate) is available as `failed_block.entry`"
            ),
            start_line=entry.start_line,
            raw=entry.raw,
            ignore_error_block=entry,
        )
        self._duplicate_keys: Set[str] = duplicate_keys

    @property
    def duplicate_keys(self) -> Set[str]:
        """The field-keys that occurred more than once in the entry."""
        return self._duplicate_keys
