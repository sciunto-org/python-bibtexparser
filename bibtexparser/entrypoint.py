import codecs
import warnings
from typing import Iterable
from typing import List
from typing import Optional
from typing import TextIO
from typing import Union

from .library import Library
from .middlewares.middleware import Middleware
from .middlewares.parsestack import default_parse_stack
from .middlewares.parsestack import default_unparse_stack
from .splitter import Splitter
from .writer import BibtexFormat
from .writer import write


def _build_parse_stack(
    parse_stack: Optional[Iterable[Middleware]],
    append_middleware: Optional[Iterable[Middleware]],
) -> List[Middleware]:
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

    parse_stack_types = [type(m) for m in parse_stack]
    append_stack_types = {type(m) for m in append_middleware}
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
            "Provided both unparse_stack and prepend_middleware. "
            "Only one should be provided. "
            "(prepend_middleware should only be used with the default unparse_stack, "
            "i.e., when the passed unparse_stack is None.)"
        )

    if unparse_stack is None:
        unparse_stack = default_unparse_stack(allow_inplace_modification=False)

    if prepend_middleware is None:
        return list(unparse_stack)

    parse_stack_types = [type(m) for m in unparse_stack]
    append_stack_types = {type(m) for m in prepend_middleware}
    stack_types_intersect = set(parse_stack_types).intersection(append_stack_types)
    if len(stack_types_intersect) > 0:
        warnings.warn(
            "Some middleware passed in append_middleware are "
            f"already in the default parse_stack ({stack_types_intersect})."
        )

    return list(prepend_middleware) + list(unparse_stack)


def _handle_deprecated_write_params(
    unparse_stack: Optional[Iterable[Middleware]],
    prepend_middleware: Optional[Iterable[Middleware]],
    kwargs: dict,
    function_name: str,
) -> tuple[Optional[Iterable[Middleware]], Optional[Iterable[Middleware]]]:
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
    parse_stack: Optional[Iterable[Middleware]] = None,
    append_middleware: Optional[Iterable[Middleware]] = None,
    library: Optional[Library] = None,
):
    """Parse a BibTeX string.

    :param bibtex_str: BibTeX string to parse
    :param parse_stack:
        List of middleware to apply to the database after splitting.
        If ``None`` (default), a default stack will be used providing simple standard functionality.

    :param append_middleware:
        List of middleware to append to the default stack
        (ignored if a not-``None`` parse_stack is passed).

    :param library:
        Library to add entries to. If ``None`` (default), a new library will be created.

    :return: Library: Parsed BibTeX database
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
    file: Union[str, TextIO],
    library: Library,
    unparse_stack: Optional[Iterable[Middleware]] = None,
    prepend_middleware: Optional[Iterable[Middleware]] = None,
    bibtex_format: Optional[BibtexFormat] = None,
    encoding: str = "UTF-8",
    **kwargs,
) -> None:
    """Write a BibTeX database to a file.

    :param file: File to write to. Can be a file name or a file object.
    :param library: BibTeX database to serialize.
    :param unparse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param prepend_middleware: List of middleware to prepend to the default stack.
                        Only applicable if `unparse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional).
    :param encoding: Encoding of the .bib file. Default encoding is ``"UTF-8"``.

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
    unparse_stack: Optional[Iterable[Middleware]] = None,
    prepend_middleware: Optional[Iterable[Middleware]] = None,
    bibtex_format: Optional["BibtexFormat"] = None,
    **kwargs,
) -> str:
    """Serialize a BibTeX database to a string.

    :param library: BibTeX database to serialize.
    :param unparse_stack: List of middleware to apply to the database before writing.
                        If None, a default stack will be used.
    :param prepend_middleware: List of middleware to prepend to the default stack.
                        Only applicable if `unparse_stack` is None.
    :param bibtex_format: Customized BibTeX format to use (optional).

    .. deprecated:: (next version)
        Parameters 'parse_stack' and 'append_middleware' are deprecated.
        Use 'unparse_stack' and 'prepend_middleware' instead.
    """
    unparse_stack, prepend_middleware = _handle_deprecated_write_params(
        unparse_stack, prepend_middleware, kwargs, "write_string"
    )

    middleware: Middleware
    for middleware in _build_unparse_stack(unparse_stack, prepend_middleware):
        library = middleware.transform(library=library)

    return write(library, bibtex_format=bibtex_format)
