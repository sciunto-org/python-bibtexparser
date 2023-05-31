import warnings
from typing import Iterable, List, Optional, TextIO, Union

from .library import Library
from .middlewares.middleware import Middleware
from .middlewares.parsestack import default_parse_stack, default_unparse_stack
from .splitter import Splitter
from .writer import BibtexFormat, write


def _build_parse_stack(
    parse_stack: Optional[Iterable[Middleware]],
    append_middleware: Optional[Iterable[Middleware]],
) -> List[Middleware]:
    if parse_stack is not None and append_middleware is not None:
        raise ValueError(
            "Provided both parse_stack and append_middleware."
            "Only one should be provided."
            "(append_middleware should only be used with the default parse_stack,"
            "i.e., when the passed parse_stack is None.)"
        )

    if parse_stack is None:
        parse_stack = default_parse_stack(allow_inplace_modification=True)

    if append_middleware is None:
        return list(parse_stack)

    parse_stack_types = [type(m) for m in parse_stack]
    append_stack_types = set([type(m) for m in append_middleware])
    stack_types_intersect = set(parse_stack_types).intersection(append_stack_types)
    if len(stack_types_intersect) > 0:
        warnings.warn(
            "Some middleware passed in append_middleware are "
            f"already in the default parse_stack ({stack_types_intersect})."
        )

    return list(parse_stack) + list(append_middleware)


def _build_unparse_stack(
    unparse_stack: Optional[Iterable[Middleware]],
    prepend_middleware: Optional[Iterable[Middleware]],
) -> List[Middleware]:
    if unparse_stack is not None and prepend_middleware is not None:
        raise ValueError(
            "Provided both parse_stack and append_middleware."
            "Only one should be provided."
            "(prepend_middleware should only be used with the default parse_stack,"
            "i.e., when the passed parse_stack is None.)"
        )

    if unparse_stack is None:
        unparse_stack = default_unparse_stack(allow_inplace_modification=False)

    if prepend_middleware is None:
        return list(unparse_stack)

    parse_stack_types = [type(m) for m in unparse_stack]
    append_stack_types = set([type(m) for m in prepend_middleware])
    stack_types_intersect = set(parse_stack_types).intersection(append_stack_types)
    if len(stack_types_intersect) > 0:
        warnings.warn(
            "Some middleware passed in append_middleware are "
            f"already in the default parse_stack ({stack_types_intersect})."
        )

    return list(prepend_middleware) + list(unparse_stack)


def parse_string(
    bibtex_str: str,
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
    library: Optional[Library] = None,
):
    """Parse a BibTeX string.

    Args:
        bibtex_str (str): BibTeX string to parse
        parse_stack (Optional[Iterable[Middleware]], optional): List of middleware to apply to the database after splitting. If None (default), a default stack will be used providing simple standard functionality will be used.
        append_middleware (Optional[Iterable[Middleware]], optional): List of middleware to append to the default stack (ignored if a not-None parse_stack is passed).
        library (Optional[Library], optional): Library to add entries to. If None (default), a new library will be created.

    Returns:
        Library: Parsed BibTeX database
    """
    splitter = Splitter(bibstr=bibtex_str)
    library = splitter.split(library=library)

    middleware: Middleware
    for middleware in _build_parse_stack(parse_stack, append_middleware):
        library = middleware.transform(library=library)

    return library


def parse_file(
    path: str,
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
) -> Library:
    """Parse a BibTeX file

    Args:
        path (str): Path to BibTeX file
        parse_stack (Optional[Iterable[Middleware]], optional): List of middleware to apply to the database after splitting. If None (default), a default stack will be used providing simple standard functionality will be used.
        append_middleware (Optional[Iterable[Middleware]], optional): List of middleware to append to the default stack (ignored if a not-None parse_stack is passed).

    Returns:
        Library: Parsed BibTeX library
    """
    with open(path) as f:
        bibtex_str = f.read()
        return parse_string(
            bibtex_str, parse_stack=parse_stack, append_middleware=append_middleware
        )


def write_file(
    file: Union[str, TextIO],
    library: Library,
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
    bibtex_format: Optional[BibtexFormat] = None,
) -> None:
    """Write a BibTeX database to a file.

    :param file: File to write to. Can be a file name or a file object.
    :param library: BibTeX database to serialize.
    :param parse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param append_middleware: List of middleware to append to the default stack.
                        Only applicable if `parse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional)."""
    bibtex_str = write_string(
        library=library,
        unparse_stack=parse_stack,
        prepend_middleware=append_middleware,
        bibtex_format=bibtex_format,
    )
    if isinstance(file, str):
        with open(file, "w") as f:
            f.write(bibtex_str)
    else:
        file.write(bibtex_str)


def write_string(
    library: Library,
    unparse_stack: Optional[Iterable[Middleware]] = None,
    prepend_middleware: Optional[Iterable[Middleware]] = None,
    bibtex_format: Optional["BibtexFormat"] = None,
) -> str:
    """Serialize a BibTeX database to a string.

    :param library: BibTeX database to serialize.
    :param unparse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param prepend_middleware: List of middleware to prepend to the default stack.
                        Only applicable if `parse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional).
    """
    middleware: Middleware
    for middleware in _build_unparse_stack(unparse_stack, prepend_middleware):
        library = middleware.transform(library=library)

    return write(library, bibtex_format=bibtex_format)
