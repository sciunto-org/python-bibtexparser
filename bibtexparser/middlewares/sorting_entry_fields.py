from typing import Tuple

from bibtexparser.library import Library
from bibtexparser.model import Block, Entry

from .middleware import BlockMiddleware


class SortFieldsAlphabeticallyMiddleware(BlockMiddleware):
    """Sorts the fields of an entry alphabetically by key."""

    def __init__(self, allow_inplace_modification: bool = True):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: Library) -> Block:
        entry.fields = sorted(entry.fields, key=lambda f: f.key)
        entry.parser_metadata[self.metadata_key()] = True
        return entry

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "sorted_fields_alphabetically"


class SortFieldsCustomMiddleware(BlockMiddleware):
    """Sorts the fields of an entry according to a custom order provided by user.

    The order is a list of field keys. Fields not in the list are put at the end."""

    def __init__(
        self,
        order: Tuple[str, ...],
        case_sensitive: bool = False,
        allow_inplace_modification: bool = True,
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )
        self._case_sensitive = case_sensitive
        if not case_sensitive:
            self._order = [x.lower() for x in order]
        else:
            self._order = order

        if len(self._order) != len(set(self._order)):
            duplicate_keys = set([x for x in self._order if self._order.count(x) > 1])
            raise ValueError(
                "Order list must not contain duplicates. "
                "The following keys are duplicated: "
                f"{', '.join(duplicate_keys)}"
            )

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: Library) -> Block:
        def _sort_key(field):
            try:
                key = field.key.lower() if not self._case_sensitive else field.key
                return self._order.index(key)
            except ValueError:
                # If the field is not in the order list, put it at the end
                return len(self._order)

        entry.fields = sorted(entry.fields, key=_sort_key)
        entry.parser_metadata[self.metadata_key()] = self._order
        return entry

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "sorted_fields_custom"
