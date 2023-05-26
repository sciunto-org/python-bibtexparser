from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Tuple, Type

from bibtexparser.library import Library
from bibtexparser.model import (
    Block,
    Entry,
    ExplicitComment,
    ImplicitComment,
    Preamble,
    String,
)

from .middleware import LibraryMiddleware

DEFAULT_BLOCK_TYPE_ORDER = (String, Preamble, Entry, ImplicitComment, ExplicitComment)


@dataclass
class _BlockJunk:
    """Data-Structure reflecting zero or more comments together with a block."""

    sort_key: str = ""
    # The blocks (comments and the main block) are stored in the order they were parsed.
    blocks: List[Block] = field(default_factory=list)

    @property
    def main_block_type(self) -> type:
        """Returns the type of the main (i.e., non-comment) block."""
        try:
            return type(self.blocks[-1])
        except IndexError:
            raise RuntimeError(
                "Block junk must contain at least one block. "
                "This is a bug in bibtexparser, please report it."
            )


class SortBlocksByTypeAndKeyMiddleware(LibraryMiddleware):
    """Sorts the blocks of a library by type and key. Optionally, comments remain above same block."""

    def __init__(
        self,
        block_type_order: Tuple[Type[Block], ...] = DEFAULT_BLOCK_TYPE_ORDER,
        preserve_comments_on_top: bool = True,
    ):
        self._verify_all_types_are_block_types(block_type_order)
        self._block_type_order = block_type_order
        self._preserve_comments_on_top = preserve_comments_on_top

        # In-place modification is not yet supported, we make this explicit here,
        super().__init__(allow_inplace_modification=False)

    @staticmethod
    def _verify_all_types_are_block_types(sort_order):
        for t in sort_order:
            if not issubclass(t, Block):
                raise ValueError(
                    "Sort order must only contain Block subclasses, "
                    f"but got {str(t)}"
                )

    @staticmethod
    def _block_junks(blocks: List[Block]) -> List[_BlockJunk]:
        block_junks = []
        current_junk = _BlockJunk()
        for block in blocks:
            current_junk.blocks.append(block)
            try:
                current_junk.sort_key = block.key
            except AttributeError:
                # Block has no key that could be used as sort key
                #   (this happens for comments, preambles and parsing-failed blocks, for example)
                pass

            if not (
                isinstance(block, ExplicitComment) or isinstance(block, ImplicitComment)
            ):
                # We added a non-comment block, hence we finish the junk and
                # start a new one
                block_junks.append(current_junk)
                current_junk = _BlockJunk()

        if current_junk.blocks:
            # That would be a junk with only comments, but we add it at the end for completeness
            block_junks.append(current_junk)

        return block_junks

    # docstr-coverage: inherited
    def transform(self, library: Library) -> Library:
        blocks = deepcopy(library.blocks)
        if self._preserve_comments_on_top:
            block_junks = self._block_junks(blocks)

            def _sort_key(block_junk):
                """Sort key for block junks. Based on (block type, string-or-entry-key)."""
                try:
                    return (
                        self._block_type_order.index(block_junk.main_block_type),
                        block_junk.sort_key,
                    )
                except ValueError:
                    # If the block type is not in the order list, put it at the end
                    return len(self._block_type_order), block_junk.sort_key

            block_junks.sort(key=_sort_key)
            return Library(
                blocks=[
                    block for block_junk in block_junks for block in block_junk.blocks
                ]
            )
        else:

            def _sort_key(block: Block):
                """Sort key for blocks. Based on (block type, string-or-entry-key)."""
                block_key = getattr(block, "key", "")
                try:
                    return self._block_type_order.index(block.__class__), block_key
                except ValueError:
                    # If the block type is not in the order list, put it at the end
                    return len(self._block_type_order), block_key

            blocks.sort(key=_sort_key)
            return Library(blocks=blocks)
