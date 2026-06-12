from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import List
from typing import Tuple
from typing import Type

from bibtexparser.library import Library
from bibtexparser.model import Block
from bibtexparser.model import Entry
from bibtexparser.model import ExplicitComment
from bibtexparser.model import ImplicitComment
from bibtexparser.model import Preamble
from bibtexparser.model import String

from .middleware import LibraryMiddleware

DEFAULT_BLOCK_TYPE_ORDER = (String, Preamble, Entry, ImplicitComment, ExplicitComment)


@dataclass
class _BlockChunk:
    """Data-Structure reflecting zero or more comments together with a block."""

    # The blocks (comments and the main block) are stored in the order they were parsed.
    blocks: List[Block] = field(default_factory=list)

    @property
    def main_block(self) -> Block:
        """Returns the main (i.e., last, non-comment) block of this chunk."""
        try:
            return self.blocks[-1]
        except IndexError:
            raise RuntimeError(
                "Block chunk must contain at least one block. "
                "This is a bug in bibtexparser, please report it."
            )


class SortBlocksMiddleware(LibraryMiddleware):
    """Sorts the blocks of a library by a user-provided sort key.

    This middleware works like Pythons built-in sorting
    (the ``key`` and ``reverse`` arguments behave as in :func:`sorted`):
    The ``key`` callable is applied to each block and the blocks are
    sorted by the returned values.

    Example: To sort entries by their ``year`` field, with all non-entry
    blocks (strings, preambles, ...) and year-less entries on top::

        from bibtexparser.middlewares import SortBlocksMiddleware
        from bibtexparser.model import Entry

        def by_year(block):
            if isinstance(block, Entry) and "year" in block:
                return (1, int(block["year"]))
            return (0, 0)

        middleware = SortBlocksMiddleware(key=by_year)

    Hints regarding the ``key`` callable:

    - It must accept every block it may be called with (see below)
      and the returned values must be mutually comparable.
      Returning tuples - as in the example above - is a simple way
      to achieve this for libraries with mixed block types,
      and also allows hierarchical sorting criteria.
    - The sort is stable: blocks for which the key returns equal values
      remain in their original relative order.
    - The key should be pure (deterministic and without side-effects).
    - If you have a comparator function (``compare(block_1, block_2) -> int``)
      instead of a key function, wrap it with :func:`functools.cmp_to_key`.

    Comment handling: if ``preserve_comments_on_top`` is True (default),
    comments remain directly above the consecutive non-comment block
    and the key is only called with said non-comment block.
    (Exception: for comments at the very end of the library - not followed
    by any non-comment block - the key is called with the last comment.)
    If ``preserve_comments_on_top`` is False, comments are sorted
    like all other blocks, and the key must thus handle comment blocks, too.
    """

    def __init__(
        self,
        key: Callable[[Block], Any],
        reverse: bool = False,
        preserve_comments_on_top: bool = True,
    ):
        """

        :param key: Callable mapping a block to a sort key, as in :func:`sorted`.
            See the class docstring for requirements and an example.
        :param reverse: If True, sort in descending order.
        :param preserve_comments_on_top: If True, comments remain above
            the following non-comment block (sorted as one unit).
        """
        self._key = key
        self._reverse = reverse
        self._preserve_comments_on_top = preserve_comments_on_top

        # In-place modification is not yet supported, we make this explicit here,
        super().__init__(allow_inplace_modification=False)

    @staticmethod
    def _block_chunks(blocks: List[Block]) -> List[_BlockChunk]:
        block_chunks = []
        current_chunk = _BlockChunk()
        for block in blocks:
            current_chunk.blocks.append(block)
            if not (isinstance(block, ExplicitComment) or isinstance(block, ImplicitComment)):
                # We added a non-comment block, hence we finish the chunk and
                # start a new one
                block_chunks.append(current_chunk)
                current_chunk = _BlockChunk()

        if current_chunk.blocks:
            # That would be a chunk with only comments, but we add it at the end for completeness
            block_chunks.append(current_chunk)

        return block_chunks

    # docstr-coverage: inherited
    def transform(self, library: Library) -> Library:
        blocks = deepcopy(library.blocks)
        if self._preserve_comments_on_top:
            block_chunks = self._block_chunks(blocks)
            block_chunks.sort(key=lambda chunk: self._key(chunk.main_block), reverse=self._reverse)
            return Library(
                blocks=[block for block_chunk in block_chunks for block in block_chunk.blocks],
                fail_on_duplicate_key=False,
            )
        else:
            blocks.sort(key=self._key, reverse=self._reverse)
            return Library(blocks=blocks, fail_on_duplicate_key=False)


class SortBlocksByTypeAndKeyMiddleware(SortBlocksMiddleware):
    """Sorts the blocks of a library by type and key. Optionally, comments remain above same block."""

    def __init__(
        self,
        block_type_order: Tuple[Type[Block], ...] = DEFAULT_BLOCK_TYPE_ORDER,
        preserve_comments_on_top: bool = True,
    ):
        self._verify_all_types_are_block_types(block_type_order)
        self._block_type_order = block_type_order

        super().__init__(
            key=self._type_and_key_sort_key,
            preserve_comments_on_top=preserve_comments_on_top,
        )

    @staticmethod
    def _verify_all_types_are_block_types(sort_order):
        for t in sort_order:
            if not issubclass(t, Block):
                raise ValueError(
                    "Sort order must only contain Block subclasses, " f"but got {str(t)}"
                )

    def _type_and_key_sort_key(self, block: Block) -> Tuple[int, str]:
        """Sort key for blocks. Based on (block type, string-or-entry-key)."""
        try:
            type_index = self._block_type_order.index(type(block))
        except ValueError:
            # If the block type is not in the order list, put it at the end
            type_index = len(self._block_type_order)
        return type_index, getattr(block, "key", "")
