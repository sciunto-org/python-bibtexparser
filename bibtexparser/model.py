import abc
from typing import Any

_ALLOWED_ENCLOSINGS = (None, "{", '"', "no-enclosing")


def _validated_enclosing(enclosing: str | None) -> str | None:
    if enclosing not in _ALLOWED_ENCLOSINGS:
        raise ValueError(
            "enclosing must be one of None, '{', '\"' or 'no-enclosing', " f"not {enclosing!r}"
        )
    return enclosing


class Block(abc.ABC):
    """An abstract superclass of all top-level building blocks of a bibtex file.

    E.g. a ``@string`` block, a ``@preamble`` block, an ``@entry`` block, a comment, etc.
    """

    def __init__(
        self,
        start_line: int | None = None,
        raw: str | None = None,
        parser_metadata: dict[str, Any] | None = None,
    ):
        self._start_line_in_file = start_line
        self._raw = raw
        if parser_metadata is None:
            parser_metadata = {}
        self._parser_metadata: dict[str, Any] = parser_metadata

    @property
    def start_line(self) -> int | None:
        """The line number of the first line of this block in the parsed string."""
        return self._start_line_in_file

    @property
    def raw(self) -> str | None:
        """The raw, unmodified string (bibtex) representation of this block.

        Note: Middleware does not update this field, hence, after applying middleware
        to a library, this field may be outdated.
        """
        return self._raw

    @property
    def parser_metadata(self) -> dict[str, Any]:
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

    def get_parser_metadata(self, key: str) -> Any | None:
        """EXPERIMENTAL: get auxiliary information stored in ``parser_metadata``.

        See attribute ``parser_metadata`` for more information."""
        return self._parser_metadata.get(key, None)

    def set_parser_metadata(self, key: str, value: Any):
        """EXPERIMENTAL: set auxiliary information stored in ``parser_metadata``.

        See attribute ``parser_metadata`` for more information."""
        self._parser_metadata[key] = value

    def __eq__(self, other: object) -> bool:
        # make sure they have the same type and same content
        return (
            isinstance(other, self.__class__)
            and isinstance(self, other.__class__)
            and self.__dict__ == other.__dict__
        )

    def __hash__(self) -> int:
        # Hash on a stable subset of the attributes compared in `__eq__`
        # (equal blocks thus have equal hashes). Mutable or potentially
        # unhashable attributes (e.g. fields, parser_metadata) are excluded.
        return hash((type(self), self._start_line_in_file, self._raw))


class String(Block):
    """Bibtex Blocks of the ``@string`` type, e.g. ``@string{me = "My Name"}``."""

    def __init__(
        self,
        key: str,
        value: str,
        start_line: int | None = None,
        raw: str | None = None,
        enclosing: str | None = None,
    ):
        super().__init__(start_line, raw)
        self._key = key
        self._value = value
        self._enclosing = _validated_enclosing(enclosing)

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
        self._enclosing = None

    @property
    def enclosing(self) -> str | None:
        """The enclosing demanded when writing this string, e.g. ``'{'``.

        Allowed values are ``'{'``, ``'"'`` and ``'no-enclosing'``.
        ``None`` (the default) leaves the choice to the writing middleware
        (see ``AddEnclosingMiddleware``), which is the right choice for most use-cases.

        Note: Assigning a new ``value`` to the string resets this attribute to ``None``."""
        return self._enclosing

    @enclosing.setter
    def enclosing(self, enclosing: str | None):
        self._enclosing = _validated_enclosing(enclosing)

    def __str__(self) -> str:
        return f"String (line: {self.start_line}, key: `{self.key}`): `{self.value}`"

    def __repr__(self) -> str:
        return (
            f"String(key=`{self.key}`, value=`{self.value}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class Preamble(Block):
    """Bibtex Blocks of the ``@preamble`` type, e.g. ``@preamble{This is a preamble}``."""

    def __init__(self, value: str, start_line: int | None = None, raw: str | None = None):
        super().__init__(start_line, raw)
        self._value = value

    @property
    def value(self) -> str:
        """The value of the preamble, e.g. ``blabla`` in ``@preamble{blabla}``."""
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    def __str__(self) -> str:
        return f"Preamble (line: {self.start_line}): `{self.value}`"

    def __repr__(self) -> str:
        return f"Preamble(value=`{self.value}`, " f"start_line={self.start_line}, raw=`{self.raw}`)"


class ExplicitComment(Block):
    """Bibtex Blocks of the ``@comment`` type, e.g. ``@comment{This is a comment}``."""

    def __init__(self, comment: str, start_line: int | None = None, raw: str | None = None):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        """The value of the comment, e.g. ``blabla`` in ``@comment{blabla}``."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def __str__(self) -> str:
        return f"ExplicitComment (line: {self.start_line}): `{self.comment}`"

    def __repr__(self) -> str:
        return (
            f"ExplicitComment(comment=`{self.comment}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class ImplicitComment(Block):
    """Bibtex outside of an ``@{...}`` block, which is treated as a comment."""

    def __init__(self, comment: str, start_line: int | None = None, raw: str | None = None):
        super().__init__(start_line, raw)
        self._comment = comment

    @property
    def comment(self) -> str:
        """The (possibly multi-line) comment."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def __str__(self) -> str:
        return f"ImplicitComment (line: {self.start_line}): `{self.comment}`"

    def __repr__(self) -> str:
        return (
            f"ImplicitComment(comment=`{self.comment}`, "
            f"start_line={self.start_line}, raw=`{self.raw}`)"
        )


class Field:
    """A field of a Bibtex entry, e.g. ``author = {John Doe}``."""

    def __init__(
        self,
        key: str,
        value: Any,
        start_line: int | None = None,
        enclosing: str | None = None,
    ):
        self._start_line = start_line
        self._key = key
        self._value = value
        self._enclosing = _validated_enclosing(enclosing)

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
        self._enclosing = None

    @property
    def enclosing(self) -> str | None:
        """The enclosing demanded when writing this field, e.g. ``'{'``.

        Allowed values are ``'{'``, ``'"'`` and ``'no-enclosing'``.
        ``None`` (the default) leaves the choice to the writing middleware
        (see ``AddEnclosingMiddleware``), which is the right choice for most use-cases.

        A demand of ``'no-enclosing'`` is used for values that must be written verbatim,
        such as bibtex string references (``month = jan``)
        or concatenation expressions (``pages = intro # outro``),
        where adding an enclosing would change the semantics of the value.

        Note: Assigning a new ``value`` to the field resets this attribute to ``None``."""
        return self._enclosing

    @enclosing.setter
    def enclosing(self, enclosing: str | None):
        self._enclosing = _validated_enclosing(enclosing)

    @property
    def start_line(self) -> int:
        """The line number of the first line of this field in the originally parsed string."""
        return self._start_line

    def __eq__(self, other: object) -> bool:
        # make sure they have the same type and same content
        return (
            isinstance(other, self.__class__)
            and isinstance(self, other.__class__)
            and self.__dict__ == other.__dict__
        )

    def __hash__(self) -> int:
        # Hash on a stable subset of the attributes compared in `__eq__`
        # (equal fields thus have equal hashes). The value is excluded as it
        # may be mutable or unhashable (e.g. a list after middleware was applied).
        return hash((type(self), self._start_line, self._key))

    def __str__(self) -> str:
        return f"Field (line: {self.start_line}, key: `{self.key}`): `{self.value}`"

    def __repr__(self) -> str:
        return (
            f"Field(key=`{self.key}`, value=`{self.value}`, "
            f"start_line={self.start_line}, enclosing={self._enclosing!r})"
        )


class EntryComment:
    """A Biber-style ``%`` comment positioned between fields of an entry.

    ``field_index`` records how many fields preceded the comment in the parsed
    source. It lets the canonical writer retain comments while keeping
    ``Entry.fields`` restricted to active bibliography data.
    """

    def __init__(self, comment: str, field_index: int):
        if field_index < 0:
            raise ValueError("field_index must be non-negative")
        self._comment = comment
        self._field_index = field_index

    @property
    def comment(self) -> str:
        """Content following the source line's leading ``%`` marker."""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    @property
    def field_index(self) -> int:
        """Number of active fields that preceded this comment when parsed."""
        return self._field_index

    @field_index.setter
    def field_index(self, value: int):
        if value < 0:
            raise ValueError("field_index must be non-negative")
        self._field_index = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EntryComment) and self.__dict__ == other.__dict__

    def __repr__(self) -> str:
        return f"EntryComment(comment={self.comment!r}, field_index={self.field_index})"


class Entry(Block):
    """Bibtex Blocks of the ``@entry`` type, e.g. ``@article{Cesar2013, ...}``."""

    def __init__(
        self,
        entry_type: str,
        key: str,
        fields: list[Field],
        start_line: int | None = None,
        raw: str | None = None,
        comments: list[EntryComment] | None = None,
    ):
        super().__init__(start_line, raw)
        self._entry_type = entry_type
        self._key = key
        self._fields = fields
        self._comments = [] if comments is None else comments

    @property
    def entry_type(self) -> str:
        """The type of the entry, e.g. ``article`` in ``@article{Cesar2013, ...}``."""
        return self._entry_type

    @entry_type.setter
    def entry_type(self, value: str):
        self._entry_type = value

    @property
    def key(self) -> str:
        """The key of the entry, e.g. ``Cesar2013`` in ``@article{Cesar2013, ...}``."""
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @property
    def fields(self) -> list[Field]:
        """The key-value attributes of an entry, as ``Field`` instances."""
        return self._fields

    @fields.setter
    def fields(self, value: list[Field]):
        self._fields = value

    @property
    def comments(self) -> list[EntryComment]:
        """Biber-style percent comments nested within this entry, in source order."""
        return self._comments

    @comments.setter
    def comments(self, value: list[EntryComment]):
        self._comments = value

    @property
    def fields_dict(self) -> dict[str, Field]:
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

    def pop(self, key: str, default=None) -> Field | None:
        """Removes and returns the field with the given key.

        :param key: The key of the field to remove.
        :param default: The value to return if the field does not exist."""
        try:
            field = self.fields_dict.pop(key)
        except KeyError:
            return default

        self._fields = [f for f in self._fields if f.key != key]
        return field

    def get(self, key: str, default=None) -> Field | None:
        """Returns the field with the given key, or the default value if it does not exist.

        :param key: The key of the field.
        :param default: The value to return if the field does not exist."""
        return self.fields_dict.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Dict-mimicking ``in`` operator.

        As in ``__getitem__``, ``ENTRYTYPE`` and ``ID`` are always contained.
        """
        if key in ("ENTRYTYPE", "ID"):
            return True
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

        Mirroring ``__getitem__``, the keys ``ENTRYTYPE`` and ``ID``
        set ``entry_type`` and ``key`` instead of a field.
        """
        if key == "ENTRYTYPE":
            self.entry_type = value
        elif key == "ID":
            self.key = value
        else:
            self.set_field(Field(key, value))

    def __delitem__(self, key: str) -> None:
        """Dict-mimicking index.

        This serves for partial v1.x backwards compatibility,
        as well as for a shorthand for `pop`.
        """
        self.pop(key)

    def items(self) -> list[tuple[str, Any]]:
        """Dict-mimicking, for partial v1.x backwards compatibility.

        For newly written code, it's recommended to use `entry.entry_type`,
        `entry.key` and `entry.fields` instead."""
        return [
            ("ENTRYTYPE", self.entry_type),
            ("ID", self.key),
        ] + [(f.key, f.value) for f in self.fields]

    def __str__(self) -> str:
        lines = [f"Entry (line: {self.start_line}, type: `{self.entry_type}`, key: `{self.key}`):"]
        lines.extend([f"\t`{f.key}` = `{f.value}`" for f in self.fields])
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"Entry(entry_type=`{self.entry_type}`, key=`{self.key}`, "
            f"fields=`{self.fields.__repr__()}`, start_line={self.start_line})"
        )


class ParsingFailedBlock(Block):
    """A block that could not be parsed due to some raised exception."""

    def __init__(
        self,
        error: Exception,
        start_line: int | None = None,
        raw: str | None = None,
        ignore_error_block: Block | None = None,
    ):
        super().__init__(start_line, raw)
        self._error = error
        self._ignore_error_block = ignore_error_block

    @property
    def error(self) -> Exception:
        """The exception that was raised during parsing."""
        return self._error

    @property
    def ignore_error_block(self) -> Block | None:
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
        start_line: int | None = None,
        raw: str | None = None,
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
    """An error-indicating block indicating a duplicate field key in an entry.

    The entry containing the duplicate field keys is available as
    `block.ignore_error_block`, the duplicate keys as `block.duplicate_keys`."""

    def __init__(self, duplicate_keys: set[str], entry: Entry):
        sorted_duplicate_keys = sorted(list(duplicate_keys))
        super().__init__(
            error=Exception(
                f"Duplicate field keys on entry: '{', '.join(sorted_duplicate_keys)}'. "
                f"Note: The entry (containing duplicates) is available as "
                f"`failed_block.ignore_error_block`"
            ),
            start_line=entry.start_line,
            raw=entry.raw,
            ignore_error_block=entry,
        )
        self._duplicate_keys: set[str] = duplicate_keys

    @property
    def duplicate_keys(self) -> set[str]:
        """The field-keys that occurred more than once in the entry."""
        return self._duplicate_keys
