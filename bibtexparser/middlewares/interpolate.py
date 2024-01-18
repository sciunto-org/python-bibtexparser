import warnings
from copy import deepcopy
from typing import Any

from bibtexparser.library import Library
from bibtexparser.model import Entry, Field

from .enclosing import REMOVED_ENCLOSING_KEY
from .middleware import LibraryMiddleware


def _value_is_nonstring_or_enclosed(value: Any) -> bool:
    """Check if value is an int or enclosed in curly braces."""
    if not isinstance(value, str):
        return True
    if value.startswith('"') and value.endswith('"'):
        return True
    if value.startswith("{") and value.endswith("}"):
        return True
    return False


class ResolveStringReferencesMiddleware(LibraryMiddleware):
    """Replace strings references with their values."""

    # docstr-coverage: inherited
    def __init__(self, allow_inplace_modification: bool = True):
        super().__init__(allow_inplace_modification)

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "ResolveStringReferences"

    # docstr-coverage: inherited
    def transform(self, library: Library) -> Library:
        if not self.allow_inplace_modification:
            library = deepcopy(library)

        entry: Entry
        raised_enclosing_warning = False
        for entry in library.entries:
            resolved_fields = list()
            if (
                not raised_enclosing_warning
                and REMOVED_ENCLOSING_KEY in entry.parser_metadata
            ):
                raised_enclosing_warning = True
                warnings.warn(
                    (
                        "The RemoveEnclosingMiddleware must not run before "
                        "the ResolveStringReferencesMiddleware."
                        "We continue, but string interpolation is likely to fail,"
                        "or to be too aggressive (i.e., replace too many strings)."
                    ),
                    UserWarning,
                )

            field: Field
            for field in entry.fields:
                if _value_is_nonstring_or_enclosed(field.value):
                    continue
                if field.value not in library.strings_dict:
                    continue
                field.value = library.strings_dict[field.value].value
                resolved_fields.append(field.key)

            if resolved_fields:
                entry.parser_metadata[self.metadata_key()] = resolved_fields

        return library


# TODO Middleware to replace field values with string references, if found

# TODO Middleware to resolve Crossref
