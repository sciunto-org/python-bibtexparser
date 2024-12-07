import abc
from typing import List, Literal, Tuple

from bibtexparser.model import Block, Entry, Field

from .middleware import BlockMiddleware

class _ListTransformerMiddleware(BlockMiddleware, abc.ABC):
    """Internal utility class - superclass for all name-transforming middlewares.

    :param allow_inplace_modification: See corresponding property.
    :param name_fields: The fields that contain names, considered by this middleware."""

    def __init__(
        self,
        allow_inplace_modification: bool = True,
        field_names: Tuple[str] = (),
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )
        self._field_names = field_names

    @property
    def field_names(self) -> Tuple[str]:
        """The fields that contain names, considered by this middleware."""
        return self._field_names

    @abc.abstractmethod
    def _transform_field_value(self, name):
        raise NotImplementedError("called abstract method")

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        field: Field
        
        for field in entry.fields:
            if field.key in self.field_names:
                field.value = self._transform_field_value(field.value)
        return entry


def split_comma_separated_list(string):
    """Helper function to split a list of comma separated values."""
    import re
    pattern = re.compile(r'\s*,\s*') # Remove extra spaces before and after comma
    return re.sub(pattern, ',', string).split(",")
    

class SeparateCSVLists(_ListTransformerMiddleware):
    """Middleware to separate comma-separated values in fields."""

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "separate_lists"

    # docstr-coverage: inherited
    def _transform_field_value(self, string) -> List[str]:
        return split_comma_separated_list(string)