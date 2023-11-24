from typing import Dict, List, Union

from .model import (
    Block,
    DuplicateBlockKeyBlock,
    Entry,
    ExplicitComment,
    ImplicitComment,
    ParsingFailedBlock,
    Preamble,
    String,
)

# TODO Use functools.lru_cache for library properties (which create lists when called)


class Library:
    """A collection of parsed bibtex blocks."""

    def __init__(self, blocks: Union[List[Block], None] = None):
        self._blocks = []
        self._entries_by_key = dict()
        self._strings_by_key = dict()
        if blocks is not None:
            self.add(blocks)

    def add(
        self, blocks: Union[List[Block], Block], fail_on_duplicate_key: bool = False
    ):
        """Add blocks to library.

        The adding is key-safe, i.e., it is made sure that no duplicate keys are added.
        for the same type (i.e., String or Entry). Duplicates are silently replaced with
        a DuplicateKeyBlock.

        :param blocks: Block or list of blocks to add.
        :param fail_on_duplicate_key: If True, raises ValueError if a block was replaced with a DuplicateKeyBlock.
        """
        if isinstance(blocks, Block):
            blocks = [blocks]

        _added_blocks = []
        for block in blocks:
            # This may replace block with a DuplicateEntryKeyBlock
            block = self._add_to_dicts(block)
            self._blocks.append(block)
            _added_blocks.append(block)

        if fail_on_duplicate_key:
            duplicate_keys = []
            for original, added in zip(blocks, _added_blocks):
                if not original is added and isinstance(added, DuplicateBlockKeyBlock):
                    duplicate_keys.append(added.key)

            if len(duplicate_keys) > 0:
                raise ValueError(
                    f"Duplicate keys found: {duplicate_keys}. "
                    f"Duplicate entries have been added to the library as DuplicateBlockKeyBlock."
                    f"Use `library.failed_blocks` to access them. "
                )

    def remove(self, blocks: Union[List[Block], Block]):
        """Remove blocks from library.

        :param blocks: Block or list of blocks to remove.
        :raises ValueError: If block is not in library."""
        if isinstance(blocks, Block):
            blocks = [blocks]

        for block in blocks:
            self._blocks.remove(block)
            if isinstance(block, Entry):
                del self._entries_by_key[block.key]
            elif isinstance(block, String):
                del self._strings_by_key[block.key]

    def replace(
        self, old_block: Block, new_block: Block, fail_on_duplicate_key: bool = True
    ):
        """Replace a block with another block, at the same position.

        :param old_block: Block to replace.
        :param new_block: Block to replace with.
        :param fail_on_duplicate_key: If False, adds a DuplicateKeyBlock if
                a block with new_block.key (other than old_block) already exists.
        :raises ValueError: If old_block is not in library or if fail_on_duplicate_key is True
                and a block with new_block.key (other than old_block) already exists."""
        try:
            index = self._blocks.index(old_block)
            self.remove(old_block)
        except ValueError:
            raise ValueError("Block to replace is not in library.")

        block_after_add = self._add_to_dicts(new_block)
        self._blocks.insert(index, block_after_add)

        if (
            new_block is not block_after_add
            and isinstance(block_after_add, DuplicateBlockKeyBlock)
            and fail_on_duplicate_key
        ):
            # Revert changes to old_block
            #   Don't fail on duplicate key, as this would lead to an infinite recursion
            #   (should never happen for a clean library, but could happen if the user
            #   tampered with the internals of the library).
            self.replace(block_after_add, old_block, fail_on_duplicate_key=False)
            raise ValueError("Duplicate key found.")

    @staticmethod
    def _cast_to_duplicate(
        prev_block_with_same_key: Union[Entry, String], duplicate: Union[Entry, String]
    ):
        assert isinstance(prev_block_with_same_key, type(duplicate)) or isinstance(
            duplicate, type(prev_block_with_same_key)
        ), (
            "Internal BibtexParser Error. Duplicate blocks share no common type."
            f"Found {type(prev_block_with_same_key)} and {type(duplicate)}, but both should be"
            f"either instance of String or instance of Entry."
            f"Please report this issue at the bibtexparser issue tracker.",
        )

        assert (
            prev_block_with_same_key.key == duplicate.key
        ), "Internal BibtexParser Error. Duplicate blocks have different keys."

        return DuplicateBlockKeyBlock(
            start_line=duplicate.start_line,
            raw=duplicate.raw,
            key=duplicate.key,
            previous_block=prev_block_with_same_key,
            duplicate_block=duplicate,
        )

    def _add_to_dicts(self, block):
        """Safely add block references to private dict structures.

        :param block: Block to add.
        :returns: The block that was added to the library. If a block
            of same type and with same key already existed, a
            DuplicateKeyBlock is returned (not added to dict).
        """
        if isinstance(block, Entry):
            try:
                prev_block_with_same_key = self._entries_by_key[block.key]
                block = self._cast_to_duplicate(prev_block_with_same_key, block)
            except KeyError:
                # No duplicate found
                self._entries_by_key[block.key] = block
        elif isinstance(block, String):
            try:
                prev_block_with_same_key = self._strings_by_key[block.key]
                block = self._cast_to_duplicate(prev_block_with_same_key, block)
            except KeyError:
                # No duplicate found
                self._strings_by_key[block.key] = block
        return block

    @property
    def blocks(self) -> List[Block]:
        """All blocks in the library, preserving order of insertion."""
        return self._blocks

    @property
    def failed_blocks(self) -> List[ParsingFailedBlock]:
        """All blocks that could not be parsed, preserving order of insertion."""
        return [b for b in self._blocks if isinstance(b, ParsingFailedBlock)]

    @property
    def strings(self) -> List[String]:
        """All @string blocks in the library, preserving order of insertion."""
        return list(self._strings_by_key.values())

    @property
    def strings_dict(self) -> Dict[str, String]:
        """Dict representation of all @string blocks in the library."""
        return self._strings_by_key

    @property
    def entries(self) -> List[Entry]:
        """All entry (@article, ...) blocks in the library, preserving order of insertion."""
        # Note: Taking this from the entries dict would be faster, but does not preserve order
        #   e.g. in cases where `replace` has been called.
        return [b for b in self._blocks if isinstance(b, Entry)]

    @property
    def entries_dict(self) -> Dict[str, Entry]:
        """Dict representation of all entry blocks in the library."""
        return self._entries_by_key.copy()

    @property
    def preambles(self) -> List[Preamble]:
        """All @preamble blocks in the library, preserving order of insertion."""
        return [block for block in self._blocks if isinstance(block, Preamble)]

    @property
    def comments(self) -> List[Union[ExplicitComment, ImplicitComment]]:
        """All comment blocks in the library, preserving order of insertion."""
        return [
            block
            for block in self._blocks
            if isinstance(block, (ExplicitComment, ImplicitComment))
        ]
