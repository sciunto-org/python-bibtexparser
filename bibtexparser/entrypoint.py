import warnings
from typing import Iterable, List, Optional, TextIO, Union

from bibtexparser import BibtexFormat, writer
from bibtexparser.library import Library
from bibtexparser.middlewares.default import default_parse_stack
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.splitter import Splitter


def _build_stack(
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
        parse_stack = default_parse_stack(
            allow_inplace_modification=True, allow_multithreading=True
        )

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


def parse_string(
    bibtex_str: str,
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
    library: Optional[Library] = None,
):
    splitter = Splitter(bibstr=bibtex_str)
    library = splitter.split(library=library)

    middleware: Middleware
    for middleware in _build_stack(parse_stack, append_middleware):
        library = middleware.transform(library=library)

    return library


def parse_file(
    path: str,
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
):
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
        parse_stack=parse_stack,
        append_middleware=append_middleware,
        bibtex_format=bibtex_format,
    )
    if isinstance(file, str):
        with open(file, "w") as f:
            f.write(bibtex_str)
    else:
        file.write(bibtex_str)


def write_string(
    library: Library,
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
    bibtex_format: Optional["BibtexFormat"] = None,
) -> str:
    """Serialize a BibTeX database to a string.

    :param library: BibTeX database to serialize.
    :param parse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param append_middleware: List of middleware to append to the default stack.
                        Only applicable if `parse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional)."""
    middleware: Middleware
    for middleware in _build_stack(parse_stack, append_middleware):
        library = middleware.transform(library=library)

    return writer.write_string(library, bibtex_format=bibtex_format)
