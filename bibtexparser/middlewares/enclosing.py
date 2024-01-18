from typing import Tuple, Union

from bibtexparser.model import Entry, Field, String

from .middleware import BlockMiddleware

REMOVED_ENCLOSING_KEY = "removed_enclosing"

STRINGS_CAN_BE_UNESCAPED_INTS = False
ENTRY_POTENTIALLY_INT_FIELDS = [
    "year",
    "month",
    "volume",
    "number",
    "pages",
    "edition",
    "chapter",
    "issue",
]


class RemoveEnclosingMiddleware(BlockMiddleware):
    """Remove enclosing characters from values such as field and strings.

    This middleware removes enclosing characters from a field value.
    It is useful when the field value is enclosed in braces or quotes
    (which is the case for the vast majority of values).

    Note: If you want to interpolate strings, you should do so
    before removing any enclosing.
    """

    def __init__(self, allow_inplace_modification: bool = True):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return REMOVED_ENCLOSING_KEY

    @staticmethod
    def _strip_enclosing(value: str) -> Tuple[str, Union[str, None]]:
        value = value.strip()
        if value.startswith("{") and value.endswith("}"):
            return value[1:-1], "{"
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1], '"'
        return value, "no-enclosing"

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: "Library") -> Entry:
        field: Field
        metadata = dict()
        for field in entry.fields:
            stripped, enclosing = self._strip_enclosing(field.value)
            field.value = stripped
            metadata[field.key] = enclosing
        entry.parser_metadata[self.metadata_key()] = metadata
        return entry

    # docstr-coverage: inherited
    def transform_string(self, string: String, library: "Library") -> String:
        stripped, enclosing = self._strip_enclosing(string.value)
        string.value = stripped
        string.parser_metadata[self.metadata_key()] = enclosing
        return string


class AddEnclosingMiddleware(BlockMiddleware):
    """Add enclosing characters to values such as field and strings.

    This middleware adds enclosing characters to a field value.
    It is useful when the field value is enclosed in braces or quotes.
    """

    def __init__(
        self,
        reuse_previous_enclosing: bool,
        enclose_integers: bool,
        default_enclosing: str,
        allow_inplace_modification: bool = True,
    ):
        """
        :param reuse_previous_enclosing: Whether to reuse the previous enclosing character,
            i.e., the enclosing removed by the RemoveEnclosingMiddleware.
            (this has precedence over the default_enclosing)
        :param enclose_integers: Whether to enclose integers
            (only of no previous enclosing was applied)
        :param default_enclosing: The default enclosing character to use ('{', '"', or 'no-enclosing')
            (only of no previous enclosing was applied, and - for ints - enclose_integers is False)
        :param allow_inplace_modification: Whether to allow inplace modification
            (see BlockMiddleware docs).
        """
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

        if default_enclosing not in ("{", '"'):
            raise ValueError(
                "default_enclosing must be either '{' or '\"'"
                f"not '{default_enclosing}'"
            )
        self._default_enclosing = default_enclosing
        self._reuse_previous_enclosing = reuse_previous_enclosing
        self._enclose_integers = enclose_integers

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "remove_enclosing"

    def _enclose(
        self, value: str, metadata_enclosing: str, apply_int_rule: bool
    ) -> str:
        enclosing = self._default_enclosing
        if self._reuse_previous_enclosing and metadata_enclosing is not None:
            enclosing = metadata_enclosing
        elif apply_int_rule and not self._enclose_integers and value.isdigit():
            return value

        if enclosing == "{":
            return f"{{{value}}}"
        if enclosing == '"':
            return f'"{value}"'
        if enclosing == "no-enclosing":
            return value
        raise ValueError(
            f"enclosing must be either '{{' or '\"' or 'no-enclosing', "
            f"not '{enclosing}'"
        )

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        field: Field
        metadata_enclosing = entry.parser_metadata.pop(
            RemoveEnclosingMiddleware.metadata_key(), None
        )
        for field in entry.fields:
            apply_int_rule = field.key in ENTRY_POTENTIALLY_INT_FIELDS
            prev_encoding = (
                metadata_enclosing.get(field.key, None)
                if metadata_enclosing is not None
                else None
            )
            field.value = self._enclose(
                field.value, prev_encoding, apply_int_rule=apply_int_rule
            )
        return entry

    # docstr-coverage: inherited
    def transform_string(self, string: String, *args, **kwargs) -> String:
        metadata_key = RemoveEnclosingMiddleware.metadata_key()
        string.value = self._enclose(
            string.value,
            string.parser_metadata.get(metadata_key),
            apply_int_rule=STRINGS_CAN_BE_UNESCAPED_INTS,
        )
        return string
