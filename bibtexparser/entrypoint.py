import codecs
import logging
import warnings
from collections.abc import Iterable
from copy import deepcopy
from typing import Optional
from typing import TextIO

from .library import Library
from .middlewares.enclosing import REMOVED_ENCLOSING_KEY
from .middlewares.middleware import Middleware
from .middlewares.parsestack import default_parse_stack
from .middlewares.parsestack import default_unparse_stack
from .model import Block
from .model import String
from .splitter import Splitter
from .writer import BibtexFormat
from .writer import write

logger = logging.getLogger(__name__)

#: Marks a seeded copy of a pre-existing `@string`, dropped before merging back.
_PREEXISTING_STRING_KEY = "bibtexparser_preexisting_string"

#: Number of blocks from which on `write_string`/`write_file` warn if the unparse
#: stack deep-copies blocks. Copying costs roughly 30-60 µs per entry, i.e. it
#: starts to dominate the write time at this size.
LARGE_LIBRARY_WARNING_THRESHOLD = 10_000


def _build_parse_stack(
    parse_stack: Iterable[Middleware] | None,
    append_middleware: Iterable[Middleware] | None,
) -> list[Middleware]:
    # Materialize upfront: the arguments may be one-shot iterators.
    parse_stack = None if parse_stack is None else list(parse_stack)
    append_middleware = None if append_middleware is None else list(append_middleware)

    if parse_stack is not None and append_middleware is not None:
        raise ValueError(
            "Provided both parse_stack and append_middleware. "
            "Only one should be provided. "
            "(append_middleware should only be used with the default parse_stack, "
            "i.e., when the passed parse_stack is None.)"
        )

    if parse_stack is None:
        parse_stack = default_parse_stack(allow_inplace_modification=True)

    if append_middleware is None:
        return list(parse_stack)

    parse_stack_types = {type(m) for m in parse_stack}
    append_stack_types = {type(m) for m in append_middleware}
    stack_types_intersect = parse_stack_types.intersection(append_stack_types)
    if len(stack_types_intersect) > 0:
        warnings.warn(
            "Some middleware passed in append_middleware are "
            f"already in the default parse_stack ({stack_types_intersect})."
        )

    return list(parse_stack) + list(append_middleware)


def _build_unparse_stack(
    unparse_stack: Iterable[Middleware] | None,
    prepend_middleware: Iterable[Middleware] | None,
) -> list[Middleware]:
    # Materialize upfront: the arguments may be one-shot iterators.
    unparse_stack = None if unparse_stack is None else list(unparse_stack)
    prepend_middleware = None if prepend_middleware is None else list(prepend_middleware)

    if unparse_stack is not None and prepend_middleware is not None:
        raise ValueError(
            "Provided both unparse_stack and prepend_middleware. "
            "Only one should be provided. "
            "(prepend_middleware should only be used with the default unparse_stack, "
            "i.e., when the passed unparse_stack is None.)"
        )

    if unparse_stack is None:
        unparse_stack = default_unparse_stack(allow_inplace_modification=False)

    if prepend_middleware is None:
        return list(unparse_stack)

    parse_stack_types = {type(m) for m in unparse_stack}
    append_stack_types = {type(m) for m in prepend_middleware}
    stack_types_intersect = parse_stack_types.intersection(append_stack_types)
    if len(stack_types_intersect) > 0:
        warnings.warn(
            "Some middleware passed in prepend_middleware are "
            f"already in the default unparse_stack ({stack_types_intersect})."
        )

    return list(prepend_middleware) + list(unparse_stack)


def _warn_if_large_library_is_copied(library: Library, unparse_stack: list[Middleware]) -> None:
    """Warn if writing ``library`` will deep-copy its blocks and that is likely slow.

    Middlewares with ``allow_inplace_modification=False`` (the default unparse stack
    is built that way) deep-copy every block they transform, which dominates the
    write time of large libraries.
    """
    n_blocks = len(library.blocks)
    if n_blocks < LARGE_LIBRARY_WARNING_THRESHOLD:
        return
    if all(middleware.allow_inplace_modification for middleware in unparse_stack):
        return
    logger.warning(
        f"Writing a library with {n_blocks} blocks: the unparse stack deep-copies blocks "
        "(it contains middlewares with allow_inplace_modification=False), "
        "which is slow for large libraries. "
        "If you do not need the library after writing, pass an unparse stack whose "
        "middlewares all allow in-place modification, e.g. "
        "`unparse_stack=bibtexparser.middlewares.default_unparse_stack("
        "allow_inplace_modification=True)`."
    )


def _handle_deprecated_write_params(
    unparse_stack: Iterable[Middleware] | None,
    prepend_middleware: Iterable[Middleware] | None,
    kwargs: dict,
    function_name: str,
) -> tuple[Iterable[Middleware] | None, Iterable[Middleware] | None]:
    """Handle deprecated parameter names for write functions.

    :param unparse_stack: Current unparse_stack value
    :param prepend_middleware: Current prepend_middleware value
    :param kwargs: Dictionary of keyword arguments to check for deprecated params
    :param function_name: Name of the calling function (for error messages)
    :return: Tuple of (unparse_stack, prepend_middleware) with deprecated values migrated
    """
    if "parse_stack" in kwargs:
        warnings.warn(
            "Parameter 'parse_stack' is deprecated. Use 'unparse_stack' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        if unparse_stack is not None:
            raise ValueError(
                "Cannot provide both 'parse_stack' (deprecated) and 'unparse_stack'. "
                "Use 'unparse_stack' instead."
            )
        unparse_stack = kwargs.pop("parse_stack")

    if "append_middleware" in kwargs:
        warnings.warn(
            "Parameter 'append_middleware' is deprecated. Use 'prepend_middleware' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        if prepend_middleware is not None:
            raise ValueError(
                "Cannot provide both 'append_middleware' (deprecated) and 'prepend_middleware'. "
                "Use 'prepend_middleware' instead."
            )
        prepend_middleware = kwargs.pop("append_middleware")

    if kwargs:
        raise TypeError(f"{function_name}() got unexpected keyword arguments: {', '.join(kwargs)}")

    return unparse_stack, prepend_middleware


def parse_string(
    bibtex_str: str,
    parse_stack: Iterable[Middleware] | None = None,
    append_middleware: Iterable[Middleware] | None = None,
    library: Library | None = None,
) -> Library:
    """Parse a BibTeX string.

    :param bibtex_str: BibTeX string to parse
    :param parse_stack:
        List of middleware to apply to the database after splitting.
        If ``None`` (default), a default stack will be used providing simple standard functionality.

    :param append_middleware:
        List of middleware to append to the default stack
        (ignored if a not-``None`` parse_stack is passed).

    :param library:
        Library to add the newly parsed blocks to.
        If ``None`` (default), a new library is created and returned.
        If a library is passed, it is returned (mutated) and:

        - the parse stack is applied **only** to the newly parsed blocks;
          blocks already contained in the passed library are left untouched
          (they were already transformed when they were parsed);
        - ``@string`` blocks already contained in the passed library are visible
          to the parse stack, i.e. string references in ``bibtex_str`` resolve
          against them (unless ``bibtex_str`` redefines the same key);
        - keys defined both in the passed library and in ``bibtex_str``
          do not raise, but yield ``DuplicateBlockKeyBlock`` instances
          (see ``library.failed_blocks``), just like duplicates within a single string.

    :return: Library: Parsed BibTeX database
    """
    splitter = Splitter(bibstr=bibtex_str)
    parsed = splitter.split()

    _seed_preexisting_strings(parsed, library)

    middleware: Middleware
    for middleware in _build_parse_stack(parse_stack, append_middleware):
        parsed = middleware.transform(library=parsed)

    if library is None:
        return parsed

    new_blocks = [b for b in parsed.blocks if not _is_seeded_string(b)]
    library.add(new_blocks, fail_on_duplicate_key=False)
    return library


def _is_seeded_string(block: Block) -> bool:
    """True for blocks seeded by `_seed_preexisting_strings` (and their transformations)."""
    return bool(block.get_parser_metadata(_PREEXISTING_STRING_KEY))


def _restore_enclosing(string: String) -> None:
    """Make sure the value of an already-parsed string is enclosed again.

    The parse stack expects freshly split (i.e. still enclosed) values.
    Feeding it an already-stripped value would make that value be treated
    as an unenclosed literal (a string reference), which does not round-trip
    to valid bibtex.
    """
    enclosing = string.parser_metadata.pop(REMOVED_ENCLOSING_KEY, None)
    if string.enclosing == "no-enclosing" or enclosing == "no-enclosing":
        return
    value = string.value
    if not isinstance(value, str):
        return
    if enclosing is None and (
        (value.startswith("{") and value.endswith("}"))
        or (value.startswith('"') and value.endswith('"'))
    ):
        return
    string.value = f'"{value}"' if enclosing == '"' else f"{{{value}}}"


def _seed_preexisting_strings(parsed: Library, library: Library | None) -> list[String]:
    """Make the ``@string`` blocks of an existing library visible to the parse stack.

    Copies (never the originals, which must not be transformed again) of the
    strings of ``library`` are added to ``parsed``, unless the newly parsed
    content redefines the same key. The copies are tagged so that they can be
    dropped again before merging the parsed blocks back into ``library``.

    :param parsed: The freshly split library, modified in place.
    :param library: The pre-existing library, or ``None``.
    :return: The seeded (tagged) string copies.
    """
    if library is None:
        return []

    # Bibtex string keys are case-insensitive, hence compare in lower case.
    redefined = {key.lower() for key in parsed.strings_dict}
    seeds = []
    for key, string in library.strings_dict.items():
        if key.lower() in redefined:
            continue
        seed = deepcopy(string)
        seed.set_parser_metadata(_PREEXISTING_STRING_KEY, True)
        _restore_enclosing(seed)
        seeds.append(seed)

    if seeds:
        parsed.add(seeds, fail_on_duplicate_key=False)
    return seeds


def parse_file(
    path: str,
    parse_stack: Iterable[Middleware] | None = None,
    append_middleware: Iterable[Middleware] | None = None,
    encoding: str = "UTF-8",
) -> Library:
    """Parse a BibTeX file

    :param path: Path to BibTeX file
    :param parse_stack:
        List of middleware to apply to the database after splitting.
        If ``None`` (default), a default stack will be used providing simple standard functionality.

    :param append_middleware:
        List of middleware to append to the default stack
        (ignored if a not-``None`` parse_stack is passed).

    :param encoding: Encoding of the .bib file. Default encoding is ``"UTF-8"``.
    :return: Library: Parsed BibTeX library
    :raises LookupError: If the specified encoding is not recognized.
    """
    try:
        codecs.lookup(encoding)
    except LookupError:
        raise LookupError(f"Unknown encoding: {encoding!r}")

    with open(path, encoding=encoding) as f:
        bibtex_str = f.read()
        return parse_string(
            bibtex_str, parse_stack=parse_stack, append_middleware=append_middleware
        )


def write_file(
    file: str | TextIO,
    library: Library,
    unparse_stack: Iterable[Middleware] | None = None,
    prepend_middleware: Iterable[Middleware] | None = None,
    bibtex_format: BibtexFormat | None = None,
    encoding: str = "UTF-8",
    **kwargs,
) -> None:
    """Write a BibTeX database to a file.

    The passed library is never modified, unless *every* middleware in the
    unparse stack allows in-place modification (e.g.
    ``unparse_stack=default_unparse_stack(allow_inplace_modification=True)``).

    :param file: File to write to. Can be a file name or a file object.
    :param library: BibTeX database to serialize.
    :param unparse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param prepend_middleware: List of middleware to prepend to the default stack.
                        Only applicable if `unparse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional).
    :param encoding: Encoding of the .bib file. Default encoding is ``"UTF-8"``.
    Writing a library with at least ``LARGE_LIBRARY_WARNING_THRESHOLD`` blocks logs a warning
    if the unparse stack deep-copies blocks (middlewares with ``allow_inplace_modification=False``),
    as that is slow; pass an all-in-place stack to avoid it.

    .. deprecated:: (next version)
        Parameters 'parse_stack' and 'append_middleware' are deprecated, will be deleted soon.
        Use 'unparse_stack' and 'prepend_middleware' instead.
    """
    unparse_stack, prepend_middleware = _handle_deprecated_write_params(
        unparse_stack, prepend_middleware, kwargs, "write_file"
    )

    bibtex_str = write_string(
        library=library,
        unparse_stack=unparse_stack,
        prepend_middleware=prepend_middleware,
        bibtex_format=bibtex_format,
    )
    if isinstance(file, str):
        with open(file, "w", encoding=encoding) as f:
            f.write(bibtex_str)
    else:
        file.write(bibtex_str)


def write_string(
    library: Library,
    unparse_stack: Iterable[Middleware] | None = None,
    prepend_middleware: Iterable[Middleware] | None = None,
    bibtex_format: Optional["BibtexFormat"] = None,
    **kwargs,
) -> str:
    """Serialize a BibTeX database to a string.

    The passed library is never modified, unless *every* middleware in the
    unparse stack allows in-place modification (e.g.
    ``unparse_stack=default_unparse_stack(allow_inplace_modification=True)``).

    :param library: BibTeX database to serialize.
    :param unparse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param prepend_middleware: List of middleware to prepend to the default stack.
                        Only applicable if `unparse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional).
    Writing a library with at least ``LARGE_LIBRARY_WARNING_THRESHOLD`` blocks logs a warning
    if the unparse stack deep-copies blocks (middlewares with ``allow_inplace_modification=False``),
    as that is slow; pass an all-in-place stack to avoid it.

    .. deprecated:: (next version)
        Parameters 'parse_stack' and 'append_middleware' are deprecated.
        Use 'unparse_stack' and 'prepend_middleware' instead.
    """
    unparse_stack, prepend_middleware = _handle_deprecated_write_params(
        unparse_stack, prepend_middleware, kwargs, "write_string"
    )

    stack = _build_unparse_stack(unparse_stack, prepend_middleware)
    _warn_if_large_library_is_copied(library, stack)
    inplace = [middleware.allow_inplace_modification for middleware in stack]
    if any(inplace) and not all(inplace):
        # Some middleware would mutate the passed library before a copying
        # middleware gets to run; copy once upfront so the caller's library
        # stays untouched (an all-in-place stack is the caller's explicit opt-in).
        library = deepcopy(library)

    middleware: Middleware
    for middleware in stack:
        library = middleware.transform(library=library)

    return write(library, bibtex_format=bibtex_format)
