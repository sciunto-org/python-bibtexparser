import abc
import logging
from copy import deepcopy
from typing import Collection, Union

from bibtexparser.library import Library
from bibtexparser.model import (
    Block,
    Entry,
    ExplicitComment,
    ImplicitComment,
    Preamble,
    String,
)


class Middleware(abc.ABC):
    """Implements a function to transform a block or library.

    Abstract Class. You should extend either BlockMiddleware
    or LibraryMiddleware"""

    def __init__(
        self,
        allow_parallel_execution: bool = True,
        allow_inplace_modification: bool = True,
    ):
        """

        :param allow_inplace_modification: See corresponding property.
        :param allow_parallel_execution: See corresponding property.
        """
        self._allow_inplace_modification = allow_inplace_modification
        self._allow_parallel_execution = allow_parallel_execution

    @property
    def allow_inplace_modification(self) -> bool:
        """If true, the middleware **may** modify the block in-place.

        I.e., if true, the output of `transform` may be the same instance
        as the input. If false, new instances must be returned.
        """
        return self._allow_inplace_modification

    @property
    def allow_parallel_execution(self) -> bool:
        """True indicates that the middleware is threadsafe."""
        return self._allow_parallel_execution

    @abc.abstractmethod
    def transform(self, library: "Library") -> "Library":
        """Main entrypoint of the middleware. Applies transformation to a library."""
        raise NotImplementedError("called abstract method")


class BlockMiddleware(Middleware, abc.ABC):
    """Transforms a library on a per-block basis.

    The `BlockMiddleware` replaces a block with zero, one or more
    new (transformed) blocks.

    Changes may rely on the state of the overall library,
    but must not change the state of the library directly,
    except if `allow_inplace_modification` is true.
    """

    @classmethod
    def metadata_key(cls) -> str:
        """Identifier of the middleware.
        This key is used to identify the middleware in a blocks metadata.
        """
        return cls.__name__

    # docstr-coverage: inherited
    def transform(self, library: "Library") -> "Library":
        # TODO Multiprocessing (only for large library and if allow_multi..)
        blocks = []
        for b in library.blocks:
            transformed = self.transform_block(b, library)
            # Case 1: None. Skip it.
            if transformed is None:
                pass
            # Case 2: A single block. Add it to the list.
            elif isinstance(transformed, Block):
                blocks.append(transformed)
            # Case 3: A collection. Append all the elements.
            elif isinstance(transformed, Collection):
                # check that all the items are indeed blocks
                for item in transformed:
                    if not isinstance(item, Block):
                        raise TypeError(
                            f"Non-Block type found in transformed collection: {type(item)}"
                        )
                blocks.extend(transformed)
            # Case 4: Something else. Error.
            else:
                raise TypeError(
                    f"Illegal output type from transform_block: {type(transformed)}"
                )
        return Library(blocks=blocks)

    def transform_block(
        self, block: Block, library: "Library"
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
        self, entry: Entry, library: "Library"
    ) -> Union[Block, Collection[Block], None]:
        """Transform an entry. Called by `transform_block` if the block is an entry.

        Note: This method modifies the passed entry. For a method
        respecting the `allow_inplace_modification` property,
        you should use `transform` or `transform_block` instead.
        """
        return entry

    def transform_string(
        self, string: String, library: "Library"
    ) -> Union[Block, Collection[Block], None]:
        """Transform a string. Called by `transform_block` if the block is a string.

        Note: This method modifies the passed string. For a method
        respecting the `allow_inplace_modification` property,
        you should use `transform` or `transform_block` instead.
        """
        return string

    def transform_preamble(
        self, preamble: Preamble, library: "Library"
    ) -> Union[Block, Collection[Block], None]:
        """Transform a preamble. Called by `transform_block` if the block is a preamble.

        Note: This method modifies the passed preamble. For a method
        respecting the `allow_inplace_modification` property,
        you should use `transform` or `transform_block` instead.
        """
        return preamble

    def transform_explicit_comment(
        self, explicit_comment: ExplicitComment, library: "Library"
    ) -> Union[Block, Collection[Block], None]:
        """Transform an explicit comment. Called by `transform_block` if the block is an explicit comment.

        Note: This method modifies the passed explicit comment. For a method
        respecting the `allow_inplace_modification` property,
        you should use `transform` or `transform_block` instead.
        """
        return explicit_comment

    def transform_implicit_comment(
        self, implicit_comment: ImplicitComment, library: "Library"
    ) -> Union[Block, Collection[Block], None]:
        """Transform an implicit comment. Called by `transform_block` if the block is an implicit comment.

        Note: This method modifies the passed implicit comment. For a method
        respecting the `allow_inplace_modification` property,
        you should use `transform` or `transform_block` instead.
        """
        return implicit_comment


class LibraryMiddleware(Middleware, abc.ABC):
    """Changes an overall library at once (not just on a per-block basis).

    Examples of library-wide changes are:
    - Re-Sorting the blocks in the library.
    - Transforming the library instance to a custom subclass of Library.

    Whatever can be done in a BlockMiddleware, should be done
    in a BlockMiddleware (and not in a LibraryMiddleware),
    for performance reasons (e.g. deleting blocks, ...).
    """

    def __init__(self, allow_inplace_modification: bool = True):
        # As library middleware is run per library (not per block individually),
        #   it cannot be parallelized.
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=False,
        )

    def transform(self, library: "Library") -> "Library":
        """Transform a library.

        :param library: Library to transform.
        :return: Transformed library. If the library should not be modified,
            return a copy of the original library.
            The returned library has to be a new instance, except if
            `self.allow_inplace_modification` is True (in which case the library
            may also return the original library).
        """
        library = library if self.allow_inplace_modification else deepcopy(library)
        return library
