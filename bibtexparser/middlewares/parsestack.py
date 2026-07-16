from bibtexparser.middlewares.enclosing import AddEnclosingMiddleware
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware

from .middleware import Middleware


def default_parse_stack(allow_inplace_modification: bool = True) -> list[Middleware]:
    """The default parse stack to be applied after splitting, if not specified otherwise."""
    return [
        RemoveEnclosingMiddleware(allow_inplace_modification=allow_inplace_modification),
    ]


def default_unparse_stack(allow_inplace_modification: bool = False) -> list[Middleware]:
    """The default unparse stack to be applied before writing, if not specified otherwise."""
    return [
        AddEnclosingMiddleware(
            allow_inplace_modification=allow_inplace_modification,
            default_enclosing="{",
            reuse_previous_enclosing=False,
            enclose_integers=True,
        )
    ]
