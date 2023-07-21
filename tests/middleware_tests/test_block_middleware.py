import pytest

from bibtexparser import Library
from bibtexparser.middlewares.middleware import BlockMiddleware
from bibtexparser.model import Entry, ExplicitComment, ImplicitComment, Preamble, String

BLOCKS = [
    ExplicitComment("explicit_comment_a"),
    String("string_b", "value_b"),
    String("string_a", "value_a"),
    ImplicitComment("% implicit_comment_a"),
    ExplicitComment("explicit_comment_b"),
    Entry("article", "entry_a", fields=[]),
    ImplicitComment("% implicit_comment_b"),
    Entry("article", "entry_b", fields=[]),
    Entry("article", "entry_d", fields=[]),
    Entry("article", "entry_c", fields=[]),
    Preamble("preamble_a"),
    ImplicitComment("% implicit_comment_c"),
]


def test_returning_none_removes_block():
    class AlwaysNoneBlockMiddleware(BlockMiddleware):
        """A middleware that returns None for every block."""

        def __init__(self):
            super().__init__(
                allow_parallel_execution=True, allow_inplace_modification=True
            )

        def transform_block(self, block, library):
            return None

        def metadata_key():
            return "AlwaysNoneBlockMiddleware"

    library = Library(blocks=BLOCKS)
    library = AlwaysNoneBlockMiddleware().transform(library)

    assert library.blocks == []


def test_returning_empty_removes_block():
    class AlwaysEmptyBlockMiddleware(BlockMiddleware):
        """A middleware that returns an empty list for every block."""

        def __init__(self):
            super().__init__(
                allow_parallel_execution=True, allow_inplace_modification=True
            )

        def transform_block(self, block, library):
            return []

        def metadata_key():
            return "AlwaysEmptyBlockMiddleware"

    library = Library(blocks=BLOCKS)
    library = AlwaysEmptyBlockMiddleware().transform(library)

    assert library.blocks == []


def test_returning_singleton_keeps_block():
    class SingletonBlockMiddleware(BlockMiddleware):
        """A middleware that returns a singleton list for every block."""

        def __init__(self):
            super().__init__(
                allow_parallel_execution=True, allow_inplace_modification=True
            )

        def transform_block(self, block, library):
            return [block]

        def metadata_key():
            return "SingletonBlockMiddleware"

    library = Library(blocks=BLOCKS)
    library = SingletonBlockMiddleware().transform(library)

    assert library.blocks == BLOCKS


def test_returning_list_adds_all():
    class PrefixBlockMiddleware(BlockMiddleware):
        """A middleware that prefixes every block with a comment."""

        def __init__(self):
            super().__init__(
                allow_parallel_execution=True, allow_inplace_modification=True
            )

        def transform_block(self, block, library):
            return [ImplicitComment("% Block"), block]

        def metadata_key():
            return "PrefixBlockMiddleware"

    library = Library(blocks=BLOCKS)
    library = PrefixBlockMiddleware().transform(library)

    expected = [
        ImplicitComment("% Block"),
        ExplicitComment("explicit_comment_a"),
        ImplicitComment("% Block"),
        String("string_b", "value_b"),
        ImplicitComment("% Block"),
        String("string_a", "value_a"),
        ImplicitComment("% Block"),
        ImplicitComment("% implicit_comment_a"),
        ImplicitComment("% Block"),
        ExplicitComment("explicit_comment_b"),
        ImplicitComment("% Block"),
        Entry("article", "entry_a", fields=[]),
        ImplicitComment("% Block"),
        ImplicitComment("% implicit_comment_b"),
        ImplicitComment("% Block"),
        Entry("article", "entry_b", fields=[]),
        ImplicitComment("% Block"),
        Entry("article", "entry_d", fields=[]),
        ImplicitComment("% Block"),
        Entry("article", "entry_c", fields=[]),
        ImplicitComment("% Block"),
        Preamble("preamble_a"),
        ImplicitComment("% Block"),
        ImplicitComment("% implicit_comment_c"),
    ]

    assert library.blocks == expected

def test_returning_bool_raises_error():
    class AlwaysTrueBlockMiddleware(BlockMiddleware):
        """A middleware that returns True for every block."""
        def __init__(self):
            super().__init__(allow_parallel_execution = True, allow_inplace_modification = True)
        def transform_block(self, block, library):
            return True
        def metadata_key():
            return "AlwaysTrueBlockMiddleware"
    
    library = Library(blocks=BLOCKS)
    with pytest.raises(TypeError):
        library = AlwaysTrueBlockMiddleware().transform(library)

def test_returning_bool_list_raises_error():
    class AlwaysTrueListBlockMiddleware(BlockMiddleware):
        """A middleware that returns [True] for every block."""
        def __init__(self):
            super().__init__(allow_parallel_execution = True, allow_inplace_modification = True)
        def transform_block(self, block, library):
            return [True]
        def metadata_key():
            return "AlwaysTrueListBlockMiddleware"
    
    library = Library(blocks=BLOCKS)
    with pytest.raises(TypeError):
        library = AlwaysTrueListBlockMiddleware().transform(library)

def test_returning_generator_raises_error():
    class SingletonGeneratorBlockMiddleware(BlockMiddleware):
        """A middleware that returns a generator for every block."""
        def __init__(self):
            super().__init__(allow_parallel_execution = True, allow_inplace_modification = True)
        def transform_block(self, block, library):
            return (b for b in [block])
        def metadata_key():
            return "SingletonGeneratorBlockMiddleware"
    
    library = Library(blocks=BLOCKS)
    with pytest.raises(TypeError):
        library = SingletonGeneratorBlockMiddleware().transform(library)

