from .model import Block
from .model import DuplicateBlockKeyBlock
from .model import Entry
from .model import ExplicitComment
from .model import ImplicitComment
from .model import ParsingFailedBlock
from .model import Preamble
from .model import String

# TODO Use functools.lru_cache for library properties (which create lists when called)


class Library:
    """A collection of parsed bibtex blocks."""

    def __init__(
        self,
        blocks: list[Block] | None = None,
        fail_on_duplicate_key: bool = True,
    ):
        self._blocks = []
        self._entries_by_key = dict()
        self._strings_by_key = dict()
        if blocks is not None:
            self.add(blocks, fail_on_duplicate_key=fail_on_duplicate_key)

    def add(self, blocks: list[Block] | Block, fail_on_duplicate_key: bool = True):
        """Add blocks to library.

        The adding is key-safe, i.e., it is made sure that no duplicate keys are added
        for the same type (i.e., String or Entry). Depending on `fail_on_duplicate_key`,
        duplicates either cause a ValueError (default) or are replaced with
        a DuplicateBlockKeyBlock.

        :param blocks: Block or list of blocks to add.
        :param fail_on_duplicate_key:
            If True (default), raises ValueError on duplicate keys, leaving the
            library unchanged. If False, duplicates are silently replaced with
            DuplicateBlockKeyBlock instances, which can be inspected via
            `library.failed_blocks`. This is e.g. used when parsing, where a
            bibtex file with duplicate keys should not raise.
        :raises ValueError: If fail_on_duplicate_key is True and a duplicate key
            is found. In this case, no blocks are added to the library.
        """
        if isinstance(blocks, Block):
            blocks = [blocks]

        if fail_on_duplicate_key:
            duplicate_keys = self._find_duplicate_keys(blocks)
            if len(duplicate_keys) > 0:
                raise ValueError(
                    f"Duplicate keys found: {duplicate_keys}. "
                    f"No blocks were added to the library. "
                    f"To add duplicates as DuplicateBlockKeyBlock instances instead, "
                    f"use `library.add(blocks, fail_on_duplicate_key=False)`."
                )

        for block in blocks:
            # This may replace block with a DuplicateEntryKeyBlock
            block = self._add_to_dicts(block)
            self._blocks.append(block)

    def _find_duplicate_keys(self, blocks: list[Block]) -> list[str]:
        """Keys of blocks that would become duplicates when added to the library."""
        # Look keys up in the by-key dicts directly (rather than copying them into
        # sets), so that the cost depends only on the number of blocks being added,
        # not on the size of the library.
        duplicate_keys = []
        new_entry_keys = set()
        new_string_keys = set()
        for block in blocks:
            if isinstance(block, Entry):
                key = block.key
                if key in self._entries_by_key or key in new_entry_keys:
                    duplicate_keys.append(key)
                else:
                    new_entry_keys.add(key)
            elif isinstance(block, String):
                key = block.key
                if key in self._strings_by_key or key in new_string_keys:
                    duplicate_keys.append(key)
                else:
                    new_string_keys.add(key)
        return duplicate_keys

    def _block_index(self, block: Block, skip: set[int] | None = None) -> int:
        """Index of a block in the library, preferring identity over equality.

        :param block: Block to look up.
        :param skip: Indices to ignore, e.g. because they are already claimed
            by another block of the same (multi-block) operation.
        :raises ValueError: If block is not in library."""
        skip = set() if skip is None else skip
        for i, b in enumerate(self._blocks):
            if i not in skip and b is block:
                return i
        # No identity match; fall back to equality.
        for i, b in enumerate(self._blocks):
            if i not in skip and b == block:
                return i
        raise ValueError("Block not in library.")

    def _key_registration(
        self, block: Block, claimed: list[tuple[dict, str]]
    ) -> tuple[dict, str] | None:
        """The by-key dict and key under which a block is registered, if any.

        A block's key is mutable and may have been changed after the block was
        added to the library. The registration is thus primarily located by
        identity, and only then by the block's current key.

        :param block: Block to look up.
        :param claimed: Registrations already claimed by other blocks of the
            same operation; these are not returned a second time.
        :returns: Tuple of by-key dict and key, or None if the block is not
            registered in any by-key dict (e.g. comments or failed blocks)."""
        if isinstance(block, Entry):
            by_key = self._entries_by_key
        elif isinstance(block, String):
            by_key = self._strings_by_key
        else:
            return None

        def is_claimed(key: str) -> bool:
            """Whether this key was already claimed by an earlier block in this call."""
            return any(d is by_key and k == key for d, k in claimed)

        for key, registered in by_key.items():
            if registered is block and not is_claimed(key):
                return by_key, key
        if block.key in by_key and not is_claimed(block.key):
            return by_key, block.key
        return None

    def remove(self, blocks: list[Block] | Block):
        """Remove blocks from library.

        If equal duplicate blocks exist in the library, the exact (identical)
        instance is removed, if present; otherwise the first equal block.

        Blocks whose key was changed after they were added are removed
        correctly, i.e., they are also de-registered from the by-key
        dictionaries backing `entries_dict` and `strings_dict`.

        :param blocks: Block or list of blocks to remove.
        :raises ValueError: If a block is not in library. In this case, no
            blocks are removed from the library."""
        if isinstance(blocks, Block):
            blocks = [blocks]

        # Resolve all lookups before mutating, so a failure changes nothing.
        indices: set[int] = set()
        registrations: list[tuple[dict, str]] = []
        for block in blocks:
            indices.add(self._block_index(block, skip=indices))
            registration = self._key_registration(block, claimed=registrations)
            if registration is not None:
                registrations.append(registration)

        for index in sorted(indices, reverse=True):
            del self._blocks[index]
        for by_key, key in registrations:
            del by_key[key]

    def replace(self, old_block: Block, new_block: Block, fail_on_duplicate_key: bool = True):
        """Replace a block with another block, at the same position.

        If equal duplicate blocks exist in the library, the exact (identical)
        instance is replaced, if present; otherwise the first equal block.

        :param old_block: Block to replace.
        :param new_block: Block to replace with.
        :param fail_on_duplicate_key: If False, adds a DuplicateKeyBlock if
                a block with new_block.key (other than old_block) already exists.
        :raises ValueError: If old_block is not in library or if fail_on_duplicate_key is True
                and a block with new_block.key (other than old_block) already exists."""
        try:
            index = self._block_index(old_block)
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
    def _cast_to_duplicate(prev_block_with_same_key: Entry | String, duplicate: Entry | String):
        if not (
            isinstance(prev_block_with_same_key, type(duplicate))
            or isinstance(duplicate, type(prev_block_with_same_key))
        ):
            raise ValueError(
                "Internal BibtexParser Error. Duplicate blocks share no common type. "
                f"Found {type(prev_block_with_same_key)} and {type(duplicate)}, but both should be "
                "either instance of String or instance of Entry. "
                "Please report this issue at the bibtexparser issue tracker."
            )

        if prev_block_with_same_key.key != duplicate.key:
            raise ValueError(
                "Internal BibtexParser Error. Duplicate blocks have different keys. "
                "Please report this issue at the bibtexparser issue tracker."
            )

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
    def blocks(self) -> list[Block]:
        """All blocks in the library, preserving order of insertion."""
        return self._blocks

    @property
    def failed_blocks(self) -> list[ParsingFailedBlock]:
        """All blocks that could not be parsed, preserving order of insertion."""
        return [b for b in self._blocks if isinstance(b, ParsingFailedBlock)]

    @property
    def strings(self) -> list[String]:
        """All @string blocks in the library, preserving order of insertion."""
        return list(self._strings_by_key.values())

    @property
    def strings_dict(self) -> dict[str, String]:
        """Dict representation of all @string blocks in the library."""
        return self._strings_by_key.copy()

    @property
    def entries(self) -> list[Entry]:
        """All entry (@article, ...) blocks in the library, preserving order of insertion."""
        # Note: Taking this from the entries dict would be faster, but does not preserve order
        #   e.g. in cases where `replace` has been called.
        return [b for b in self._blocks if isinstance(b, Entry)]

    @property
    def entries_dict(self) -> dict[str, Entry]:
        """Dict representation of all entry blocks in the library."""
        return self._entries_by_key.copy()

    @property
    def preambles(self) -> list[Preamble]:
        """All @preamble blocks in the library, preserving order of insertion."""
        return [block for block in self._blocks if isinstance(block, Preamble)]

    @property
    def comments(self) -> list[ExplicitComment | ImplicitComment]:
        """All comment blocks in the library, preserving order of insertion."""
        return [
            block for block in self._blocks if isinstance(block, (ExplicitComment, ImplicitComment))
        ]
