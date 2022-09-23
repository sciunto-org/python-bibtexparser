import abc
import logging
from copy import deepcopy
from typing import Union, Collection

from bibtexparser.model import (
    Block,
    Entry,
    ExplicitComment,
    ImplicitComment,
    Preamble,
    String,
)


class BlockMiddleware(abc.ABC):
    def __init__(self, allow_inplace_modification: bool, allow_multithreading: bool):
        self._allow_inplace_modification = allow_inplace_modification
        self._allow_multithreading = allow_multithreading

    @property
    def allow_inplace_modification(self) -> bool:
        return self._allow_inplace_modification

    @property
    def allow_multithreading(self) -> bool:
        return self._allow_multithreading

    def transform(
            self, block: Block, library: 'Library'
    ) -> Union[Block, Collection[Block], None]:
        """Transform a block.

        :param block: Block to transform.
        :param library: Library containing the block.
            Should typically not be modified during
            the transformation, but be considered as read-only.
            If the library is modified, make sure to set the `allow_multithreading`
            constructor argument to false
        :return: Transformed block. If the block should be removed, return None.
            If the block should be replaced by multiple blocks, return a collection
            of blocks. If the block should be replaced by a single block, return
            the single block. If the block should not be modified, return a copy of
            the original block.
            The returned block has to be a new instance, except if
            `self.allow_inplace_modification` is True (in which case the block
            may also return the original block).
        """
        block = block if self.allow_inplace_modification else deepcopy(block)
        if isinstance(block, Entry):
            return self.transform_entry(block, library)
        elif isinstance(block, String):
            return self.transform_string(block, library)
        elif isinstance(block, Preamble):
            return self.transform_preamble(block, library)
        elif isinstance(block, ExplicitComment):
            return self.transform_explicit_comment(block, library)
        elif isinstance(block, ImplicitComment):
            return self.transform_implicit_comment(block, library)

        logging.warning(f"Unknown block type {type(block)}")
        return block

    def transform_entry(
            self, entry: Entry, library: 'Library'
    ) -> Union[Block, Collection[Block], None]:
        return entry

    def transform_string(
            self, string: String, library: 'Library'
    ) -> Union[Block, Collection[Block], None]:
        return string

    def transform_preamble(
            self, preamble: Preamble, library: 'Library'
    ) -> Union[Block, Collection[Block], None]:
        return preamble

    def transform_explicit_comment(
            self, explicit_comment: ExplicitComment, library: 'Library'
    ) -> Union[Block, Collection[Block], None]:
        return explicit_comment

    def transform_implicit_comment(
            self, implicit_comment: ImplicitComment, library: 'Library'
    ) -> Union[Block, Collection[Block], None]:
        return implicit_comment
