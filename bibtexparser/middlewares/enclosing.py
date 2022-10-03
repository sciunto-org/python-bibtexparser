from typing import Union, Tuple

from bibtexparser.middlewares.middleware import BlockMiddleware
from bibtexparser.model import ImplicitComment, ExplicitComment, String, Entry, Field


class RemoveEnclosingMiddleware(BlockMiddleware):
    """Remove enclosing characters from values such as field and strings.

    This middleware removes enclosing characters from a field value.
    It is useful when the field value is enclosed in braces or quotes
    (which is the case for the vast majority of values).

    Note: If you want to interpolate strings, you should do so
    before removing any enclosing.
    """

    def __init__(self, allow_inplace_modification: bool):
        super().__init__(allow_inplace_modification=allow_inplace_modification,
                         allow_parallel_execution=True)

    @staticmethod
    def metadata_key() -> str:
        return "removed_enclosing"

    @staticmethod
    def _strip_enclosing(value: str) -> Tuple[str, Union[str, None]]:
        """Figure out the enclosing character of a value.

        Args:
            value (str): The value to figure out the enclosing character.

        Returns:
            str: The enclosing character.
            None: If no enclosing character is found.
        """
        value = value.strip()
        if value.startswith('{') and value.endswith('}'):
            return value[1:-1], '{'
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1], '"'
        return value, "no-enclosing"

    def transform_entry(self, entry: Entry, library: 'Library') -> Entry:
        field: Field
        metadata = dict()
        for field in entry.fields:
            stripped, enclosing = self._strip_enclosing(field.value)
            field.value = stripped
            metadata[field.key] = enclosing
        entry.parser_metadata[self.metadata_key()] = metadata
        return entry

    def transform_string(self, string: String, library: 'Library') -> String:
        stripped, enclosing = self._strip_enclosing(string.value)
        string.value = stripped
        string.parser_metadata[self.metadata_key()] = enclosing
        return string

    def transform_explicit_comment(self, explicit_comment: ExplicitComment, library: 'Library') -> ExplicitComment:
        stripped, enclosing = self._strip_enclosing(explicit_comment.comment)
        explicit_comment.comment = stripped
        explicit_comment.parser_metadata[self.metadata_key()] = enclosing
        return explicit_comment

    def transform_implicit_comment(self, implicit_comment: ImplicitComment, library: 'Library') -> ImplicitComment:
        stripped, enclosing = self._strip_enclosing(implicit_comment.comment)
        implicit_comment.comment = stripped
        implicit_comment.parser_metadata[self.metadata_key()] = enclosing
        return implicit_comment


class AddEnclosingMiddleware(BlockMiddleware):
    """Add enclosing characters to values such as field and strings.

    This middleware adds enclosing characters to a field value.
    It is useful when the field value is enclosed in braces or quotes.
    """

    def __init__(self,
                 default_enclosing: str,
                 enclose_integers: bool,
                 reuse_previous_enclosing: bool,
                 allow_inplace_modification: bool):
        """
        :param default_enclosing: The default enclosing character to use.
        :param enclose_integers: Whether to enclose integers.
        :param reuse_previous_enclosing: Whether to reuse the previous enclosing character,
            i.e., the enclosing removed by the RemoveEnclosingMiddleware.
            (this has precedence over the default_enclosing)
        :param allow_inplace_modification: Whether to allow inplace modification
            (see BlockMiddleware docs).
        """
        super().__init__(allow_inplace_modification=allow_inplace_modification,
                         allow_parallel_execution=True)

        if default_enclosing not in ('{', '"'):
            raise ValueError("default_enclosing must be either '{' or '\"' or 'no-enclosing', "
                             f"not '{default_enclosing}'")
        self._default_enclosing = default_enclosing
        self._reuse_previous_enclosing = reuse_previous_enclosing
        self._enclose_integers = enclose_integers

    @staticmethod
    def metadata_key() -> str:
        return "remove_enclosing"
 
    @property
    def _potentially_int_fields(self) -> Tuple[str, ...]:
        return 'year', 'month', 'volume', 'number', 'pages', 'edition', 'chapter', 'issue'

    def _enclose(self, value: str, metadata_enclosing: str) -> str:
        enclosing = self._default_enclosing
        if self._reuse_previous_enclosing and metadata_enclosing is not None:
            enclosing = metadata_enclosing
        if enclosing == '{':
            return f'{{{value}}}'
        if enclosing == '"':
            return f'"{value}"'
        if enclosing is None:
            return value
        raise ValueError(f"enclosing must be either '{{' or '\"' or 'no-enclosing', "
                         f"not '{enclosing}'")

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Entry:
        field: Field
        metadata_enclosing = entry.parser_metadata.pop(RemoveEnclosingMiddleware.metadata_key(), default=None)
        for field in entry.fields:
            if field.key in self._potentially_int_fields and not self._enclose_integers:
                if field.value.isdigit():
                    continue
            field.value = self._enclose(field.value, metadata_enclosing.get(field.key))
        return entry

    def transform_string(self, string: String, *args, **kwargs) -> String:
        metadata_key = RemoveEnclosingMiddleware.metadata_key()
        string.value = self._enclose(string.value, string.parser_metadata.get(metadata_key))
        return string

    def transform_explicit_comment(self, explicit_comment: ExplicitComment, *args, **kwargs) -> ExplicitComment:
        metadata_key = RemoveEnclosingMiddleware.metadata_key()
        from_metadata = explicit_comment.parser_metadata.get(metadata_key)
        explicit_comment.value = self._enclose(explicit_comment.value, from_metadata)
        return explicit_comment

    def transform_implicit_comment(self, implicit_comment: ImplicitComment, *args, **kwargs) -> ImplicitComment:
        metadata_key = RemoveEnclosingMiddleware.metadata_key()
        from_metadata = implicit_comment.parser_metadata.get(metadata_key)
        implicit_comment.value = self._enclose(implicit_comment.value, from_metadata)
        return implicit_comment
