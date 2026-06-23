import warnings
from copy import deepcopy
from typing import Any

from bibtexparser.library import Library
from bibtexparser.model import Entry
from bibtexparser.model import Field

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


def _split_concatenation(value: str) -> "list[str] | None":
    """Split a value on top-level ``#`` concatenation operators.

    Returns the list of stripped tokens if the value contains at least one
    ``#`` outside of any ``"..."`` or ``{...}`` group, otherwise ``None``
    (i.e., the value is not a concatenation expression).
    """
    tokens = []
    current = []
    depth = 0
    in_quotes = False
    found_separator = False
    for char in value:
        if char == '"' and depth == 0:
            in_quotes = not in_quotes
            current.append(char)
        elif char == "{" and not in_quotes:
            depth += 1
            current.append(char)
        elif char == "}" and not in_quotes:
            depth = max(0, depth - 1)
            current.append(char)
        elif char == "#" and depth == 0 and not in_quotes:
            found_separator = True
            tokens.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if not found_separator:
        return None

    tokens.append("".join(current).strip())
    return tokens


def _resolve_concatenation(tokens: "list[str]", string_values: "dict[str, str]") -> "str | None":
    """Resolve concatenation tokens to their joined string content.

    Each token is a number (kept verbatim), a quoted or braced string (its
    inner content is used), or a string reference (resolved via
    ``string_values``). Returns ``None`` if any reference is unknown, so the
    caller can leave the original expression untouched.
    """
    resolved = []
    for token in tokens:
        if not token:
            return None
        if token.startswith('"') and token.endswith('"'):
            resolved.append(token[1:-1])
        elif token.startswith("{") and token.endswith("}"):
            resolved.append(token[1:-1])
        elif token.isdigit():
            resolved.append(token)
        else:
            try:
                referenced = string_values[token.lower()]
            except KeyError:
                return None
            if referenced.startswith(('"', "{")) and referenced.endswith(('"', "}")):
                referenced = referenced[1:-1]
            resolved.append(referenced)

    return "".join(resolved)


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

        # BibTeX string keys are case-insensitive; later definitions win.
        string_values = {key.lower(): s.value for key, s in library.strings_dict.items()}

        entry: Entry
        raised_enclosing_warning = False
        for entry in library.entries:
            resolved_fields = list()
            if not raised_enclosing_warning and REMOVED_ENCLOSING_KEY in entry.parser_metadata:
                raised_enclosing_warning = True
                warnings.warn(
                    (
                        "The RemoveEnclosingMiddleware must not run before "
                        "the ResolveStringReferencesMiddleware. "
                        "We continue, but string interpolation is likely to fail, "
                        "or to be too aggressive (i.e., replace too many strings)."
                    ),
                    UserWarning,
                )

            field: Field
            for field in entry.fields:
                if isinstance(field.value, str):
                    tokens = _split_concatenation(field.value)
                    if tokens is not None:
                        joined = _resolve_concatenation(tokens, string_values)
                        if joined is not None:
                            # Keep the result enclosed (in braces) so the
                            # downstream enclosing middlewares treat it as a
                            # plain string rather than an unenclosed reference.
                            field.value = "{" + joined + "}"
                            resolved_fields.append(field.key)
                        continue

                if _value_is_nonstring_or_enclosed(field.value):
                    continue
                try:
                    field.value = string_values[field.value.lower()]
                except KeyError:
                    continue
                resolved_fields.append(field.key)

            if resolved_fields:
                entry.parser_metadata[self.metadata_key()] = resolved_fields

        return library


# TODO Middleware to replace field values with string references, if found

# TODO Middleware to resolve Crossref
