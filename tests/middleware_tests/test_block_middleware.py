from bibtexparser import Library
from bibtexparser.model import Entry, ExplicitComment, ImplicitComment, Preamble, String
from bibtexparser.middlewares.middleware import BlockMiddleware

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
            super().__init__(allow_parallel_execution = True, allow_inplace_modification = True)
        def transform_block(self, block, library):
            return None
        def metadata_key():
            return "AlwaysNoneBlockMiddleware"
    
    library = Library(blocks=BLOCKS)
    library = AlwaysNoneBlockMiddleware().transform(library)

    assert library.blocks == []

def test_returning_list_adds_all():
    class PrefixBlockMiddleware(BlockMiddleware):
        """A middleware that prefixes every block with a comment."""
        def __init__(self):
            super().__init__(allow_parallel_execution = True, allow_inplace_modification = True)
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