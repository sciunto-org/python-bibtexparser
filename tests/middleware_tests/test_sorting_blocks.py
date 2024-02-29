from bibtexparser import Library
from bibtexparser.middlewares.sorting_blocks import SortBlocksByTypeAndKeyMiddleware
from bibtexparser.model import Entry
from bibtexparser.model import ExplicitComment
from bibtexparser.model import ImplicitComment
from bibtexparser.model import Preamble
from bibtexparser.model import String

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


def test_sorting_blocks_preserving_comments_default_type_order():
    library = Library(blocks=BLOCKS)
    library = SortBlocksByTypeAndKeyMiddleware().transform(library)
    ordered_blocks = library.blocks

    assert ordered_blocks[0] == String("string_a", "value_a")

    assert ordered_blocks[1] == ExplicitComment("explicit_comment_a")
    assert ordered_blocks[2] == String("string_b", "value_b")

    assert ordered_blocks[3] == Preamble("preamble_a")

    assert ordered_blocks[4] == ImplicitComment("% implicit_comment_a")
    assert ordered_blocks[5] == ExplicitComment("explicit_comment_b")
    assert ordered_blocks[6] == Entry("article", "entry_a", fields=[])

    assert ordered_blocks[7] == ImplicitComment("% implicit_comment_b")
    assert ordered_blocks[8] == Entry("article", "entry_b", fields=[])

    assert ordered_blocks[9] == Entry("article", "entry_c", fields=[])
    assert ordered_blocks[10] == Entry("article", "entry_d", fields=[])
    assert ordered_blocks[11] == ImplicitComment("% implicit_comment_c")

    assert len(ordered_blocks) == len(BLOCKS)


def test_sorting_blocks_preserving_comments_custom_type_order():
    type_order = (Preamble, String, Entry)
    library = Library(blocks=BLOCKS)
    library = SortBlocksByTypeAndKeyMiddleware(block_type_order=type_order).transform(library)
    ordered_blocks = library.blocks

    assert ordered_blocks[0] == Preamble("preamble_a")
    assert ordered_blocks[1] == String("string_a", "value_a")

    assert ordered_blocks[2] == ExplicitComment("explicit_comment_a")
    assert ordered_blocks[3] == String("string_b", "value_b")

    assert ordered_blocks[4] == ImplicitComment("% implicit_comment_a")
    assert ordered_blocks[5] == ExplicitComment("explicit_comment_b")
    assert ordered_blocks[6] == Entry("article", "entry_a", fields=[])

    assert ordered_blocks[7] == ImplicitComment("% implicit_comment_b")
    assert ordered_blocks[8] == Entry("article", "entry_b", fields=[])

    assert ordered_blocks[9] == Entry("article", "entry_c", fields=[])
    assert ordered_blocks[10] == Entry("article", "entry_d", fields=[])

    assert ordered_blocks[11] == ImplicitComment("% implicit_comment_c")

    assert len(ordered_blocks) == len(BLOCKS)


def test_sorting_blocks_no_comment_preserving_with_custom_order():
    type_order = (Preamble, String, Entry, ImplicitComment)
    library = Library(blocks=BLOCKS)
    library = SortBlocksByTypeAndKeyMiddleware(
        block_type_order=type_order, preserve_comments_on_top=False
    ).transform(library)
    ordered_blocks = library.blocks

    assert ordered_blocks[0] == Preamble("preamble_a")

    assert ordered_blocks[1] == String("string_a", "value_a")
    assert ordered_blocks[2] == String("string_b", "value_b")

    assert ordered_blocks[3] == Entry("article", "entry_a", fields=[])
    assert ordered_blocks[4] == Entry("article", "entry_b", fields=[])
    assert ordered_blocks[5] == Entry("article", "entry_c", fields=[])
    assert ordered_blocks[6] == Entry("article", "entry_d", fields=[])

    assert ordered_blocks[7] == ImplicitComment("% implicit_comment_a")
    assert ordered_blocks[8] == ImplicitComment("% implicit_comment_b")
    assert ordered_blocks[9] == ImplicitComment("% implicit_comment_c")

    # Types not defined in the type_order should be put at the end
    assert ordered_blocks[10] == ExplicitComment("explicit_comment_a")
    assert ordered_blocks[11] == ExplicitComment("explicit_comment_b")

    assert len(ordered_blocks) == len(BLOCKS)
