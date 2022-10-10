from copy import deepcopy
from typing import Optional

from bibtexparser.library import Library
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.model import Preamble, ImplicitComment, ExplicitComment


def assert_block_does_not_change(block_type: str,
                                 middleware: Middleware,
                                 same_instance: Optional[bool]):
    """Utility to make sure blocks of some types are not changed by middleware."""
    block_type = block_type.lower()
    if block_type == "preamble":
        block = Preamble(start_line=5, raw="@Preamble{a_x + b_x^2}", value="a_x + b_x^2")
    elif block_type == "implicit_comment":
        block = ImplicitComment(start_line=5, raw="# MyComment", comment="MyComment")
    elif block_type == "explicit_comment":
        block = ExplicitComment(start_line=5, raw="@Comment{MyComment}", comment="MyComment")
    else:
        raise ValueError("block type not yet supported in test utility")

    block_copy = deepcopy(block)

    transformed_library = middleware.transform(library=Library([block]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert transformed_library.blocks[0] == block_copy
    if same_instance:
        assert transformed_library.blocks[0] is block
    elif not same_instance:
        assert transformed_library.blocks[0] is not block
