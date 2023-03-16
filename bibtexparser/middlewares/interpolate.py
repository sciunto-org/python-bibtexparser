from copy import deepcopy
from typing import Any

from bibtexparser import Library
from bibtexparser.middlewares.middleware import LibraryMiddleware
from bibtexparser.model import Entry, Field


def _value_is_nonstring_or_enclosed(value: Any) -> bool:
    """Check if value is an int or enclosed in curly braces."""
    if not isinstance(value, str):
        return True
    if value.startswith('"') and value.endswith('"'):
        return True
    if value.startswith('{') and value.endswith('}'):
        return True
    return False


class ResolveStringReferencesMiddleware(LibraryMiddleware):
    """Replace strings references with their values."""

    # docstr-coverage: inherited
    def __init__(self, allow_inplace_modification: bool):
        super().__init__(allow_inplace_modification)

    # docstr-coverage: inherited
    def transform(self, library: Library) -> Library:
        if not self.allow_inplace_modification:
            library = deepcopy(library)

        entry: Entry
        for entry in library.entries:
            field: Field
            for field in entry.fields.values():
                if _value_is_nonstring_or_enclosed(field.value):
                    continue
                if field.value not in library.strings:
                    continue
                field.value = library.strings[field.value].value

        return library


# TODO Replace field values with string reference, if found

# TODO Crossref can be put here as well