import warnings
from copy import deepcopy
from typing import Any

from bibtexparser.library import Library
from bibtexparser.model import Entry
from bibtexparser.model import Field

from .enclosing import REMOVED_ENCLOSING_KEY
from .enclosing import _literal_content
from .enclosing import _split_concatenation
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


def _resolve_tokens(tokens: list[str], strings: dict[str, str]) -> str | None:
    """Join the resolved content of the tokens of a concatenation.

    Each token is a quoted or braced literal, a number, or a string reference.
    Returns None if any of them is unresolvable, so that the caller can keep the
    original expression instead of resolving it partially.
    """
    resolved = []
    for token in tokens:
        content = _literal_content(token)
        if content is None:
            content = token if token.isdigit() else strings.get(token.lower())
        if content is None:
            return None
        resolved.append(content)
    return "".join(resolved)


def _resolve_value(value: str, strings: dict[str, str]) -> str | None:
    """Resolve a literal, a number, a string reference or a `#` expression."""
    tokens = _split_concatenation(value)
    return _resolve_tokens([value.strip()] if tokens is None else tokens, strings)


def _resolve_string_definitions(definitions: dict[str, str]) -> dict[str, str]:
    """Resolve the content of every string definition that can be resolved.

    Definitions may reference each other, so this iterates until no further
    definition resolves. Iterating rather than recursing means that an
    arbitrarily long chain of definitions cannot exhaust the interpreter stack,
    and that definitions on a reference cycle simply never resolve.
    """
    resolved: dict[str, str] = {}
    pending = dict(definitions)
    while pending:
        progressed = False
        for key, value in list(pending.items()):
            content = _resolve_value(value, resolved)
            if content is None:
                continue
            resolved[key] = content
            del pending[key]
            progressed = True
        if not progressed:
            break
    return resolved


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
        resolved_strings = _resolve_string_definitions(string_values)

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
                        content = _resolve_tokens(tokens, resolved_strings)
                        if content is not None:
                            # Braces keep the result a plain value: unenclosed, it
                            # would be read back as a reference when written.
                            field.value = "{" + content + "}"
                            resolved_fields.append(field.key)
                        # An unresolvable expression is left exactly as it is,
                        # which the enclosing middlewares preserve.
                        continue

                if _value_is_nonstring_or_enclosed(field.value):
                    continue
                key = field.value.lower()
                try:
                    referenced = string_values[key]
                except KeyError:
                    continue

                if (
                    _split_concatenation(referenced) is not None
                    or referenced.lower() in string_values
                ):
                    # The definition is itself an expression or another reference,
                    # so it must be resolved rather than substituted verbatim.
                    content = resolved_strings.get(key)
                    if content is None:
                        continue
                    referenced = "{" + content + "}"
                field.value = referenced
                resolved_fields.append(field.key)

            if resolved_fields:
                entry.parser_metadata[self.metadata_key()] = resolved_fields

        return library


# TODO Middleware to replace field values with string references, if found

# TODO Middleware to resolve Crossref
