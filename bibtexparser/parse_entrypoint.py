from typing import Iterable, Optional

from bibtexparser.library import Library
from bibtexparser.middlewares.default import default_parse_stack
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.splitter import Splitter


def parse_string(bibtex_str: str,
                 parse_stack: Optional[Iterable[Middleware]] = None,
                 library: Optional[Library] = None):
    splitter = Splitter(bibstr=bibtex_str)
    library = splitter.split(library=library)
    if parse_stack is None:
        parse_stack = default_parse_stack(allow_inplace_modification=True,
                                          allow_multithreading=True)
    middleware: Middleware
    for middleware in parse_stack:
        library = middleware.transform(library=library)

    return library


def parse_file(path: str,
               parse_stack: Optional[Iterable[Middleware]]):
    with open(path) as f:
        bibtex_str = f.read()
        return parse_string(bibtex_str, parse_stack=parse_stack)


