from typing import List

from bibtexparser.middlewares.enclosing import (
    AddEnclosingMiddleware,
    RemoveEnclosingMiddleware,
)
from bibtexparser.middlewares.middleware import Middleware


def default_parse_stack(allow_inplace_modification: bool = True) -> List[Middleware]:
    return [
        RemoveEnclosingMiddleware(allow_inplace_modification=allow_inplace_modification)
    ]


def default_unparse_stack(allow_inplace_modification: bool = True) -> List[Middleware]:
    return [
        AddEnclosingMiddleware(
            allow_inplace_modification=allow_inplace_modification,
            default_enclosing="{",
            reuse_previous_enclosing=False,
            enclose_integers=True,
        )
    ]
