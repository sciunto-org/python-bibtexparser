from copy import deepcopy
from typing import Optional

from bibtexparser.library import Library
from bibtexparser.middlewares.middleware import Middleware
from bibtexparser.model import Block
from bibtexparser.model import ExplicitComment
from bibtexparser.model import ImplicitComment
from bibtexparser.model import Preamble


def assert_block_does_not_change(
    block_type: str, middleware: Middleware, same_instance: Optional[bool]
):
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


def assert_inplace_is_respected(inplace: bool, input_block: Block, transformed_block: Block):
    """Make sure input instance is reused if and only if `inplace` is True."""
    if inplace:
        # Note that this is not a strict requirement,
        #   as "allow_inplace" does not mandate inplace modification,
        #   but this test utility is specifically aimed for middleware
        #   which do support inplace modification (e.g. for performance reasons)
        assert transformed_block is input_block
    else:
        assert transformed_block is not input_block


def assert_nonfield_entry_attributes_unchanged(original_copy, transformed_entry):
    """Verify all attributes of entry (except `fields`) are identical."""
    assert transformed_entry.start_line == original_copy.start_line
    assert transformed_entry.raw == original_copy.raw
    assert transformed_entry.entry_type == original_copy.entry_type
    assert transformed_entry.key == original_copy.key
