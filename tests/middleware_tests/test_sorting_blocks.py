import bibtexparser
from bibtexparser import Library
from bibtexparser.middlewares.sorting_blocks import SortBlocksByTypeAndKeyMiddleware
from bibtexparser.middlewares.sorting_blocks import SortBlocksMiddleware
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


ENTRIES_BIBTEX = """
@article{newest, author = {Author, C}, year = {2020}}
@article{oldest, author = {Author, B}, year = {1999}}
@article{middle, author = {Author, A}, year = {2005}}
"""


def test_sorting_blocks_by_custom_key_year_field():
    library = bibtexparser.parse_string(ENTRIES_BIBTEX)

    library = SortBlocksMiddleware(key=lambda entry: int(entry["year"])).transform(library)

    assert [entry.key for entry in library.entries] == ["oldest", "middle", "newest"]


def test_sorting_blocks_by_custom_key_reverse():
    library = bibtexparser.parse_string(ENTRIES_BIBTEX)

    library = SortBlocksMiddleware(key=lambda entry: int(entry["year"]), reverse=True).transform(
        library
    )

    assert [entry.key for entry in library.entries] == ["newest", "middle", "oldest"]


def test_sorting_blocks_by_custom_hierarchical_key():
    bibtex = """
    @article{same_year_b, author = {Author, B}, year = {2005}}
    @article{newest, author = {Author, C}, year = {2020}}
    @article{same_year_a, author = {Author, A}, year = {2005}}
    """
    library = bibtexparser.parse_string(bibtex)

    # Sort by year first, ties broken by author
    library = SortBlocksMiddleware(
        key=lambda entry: (int(entry["year"]), entry["author"])
    ).transform(library)

    assert [entry.key for entry in library.entries] == ["same_year_a", "same_year_b", "newest"]


def test_sorting_blocks_by_custom_key_is_stable():
    bibtex = """
    @article{c, year = {2005}}
    @article{a, year = {2005}}
    @article{b, year = {2005}}
    """
    library = bibtexparser.parse_string(bibtex)

    library = SortBlocksMiddleware(key=lambda entry: int(entry["year"])).transform(library)

    # Equal sort keys: input order must be preserved (stable sort)
    assert [entry.key for entry in library.entries] == ["c", "a", "b"]


def test_sorting_blocks_by_custom_key_with_mixed_block_types():
    bibtex = """
    @article{newer, year = {2020}}
    @string{me = "My Name"}
    @article{older, year = {1999}}
    @preamble{"some preamble"}
    """

    def entries_by_year_others_on_top(block):
        # Tuple keys make mixed block types comparable:
        #   non-entries first, then entries sorted by year
        if isinstance(block, Entry):
            return (1, int(block["year"]))
        return (0, 0)

    library = bibtexparser.parse_string(bibtex)
    library = SortBlocksMiddleware(key=entries_by_year_others_on_top).transform(library)

    assert [type(block) for block in library.blocks] == [String, Preamble, Entry, Entry]
    assert [entry.key for entry in library.entries] == ["older", "newer"]


def test_sorting_blocks_by_custom_key_keeps_comments_on_top():
    bibtex = """
    % comment belonging to newer
    @article{newer, year = {2020}}
    @article{older, year = {1999}}
    """
    library = bibtexparser.parse_string(bibtex)

    library = SortBlocksMiddleware(key=lambda entry: int(entry["year"])).transform(library)

    blocks = library.blocks
    assert isinstance(blocks[0], Entry) and blocks[0].key == "older"
    assert isinstance(blocks[1], ImplicitComment)
    assert blocks[1].comment == "% comment belonging to newer"
    assert isinstance(blocks[2], Entry) and blocks[2].key == "newer"


def test_sorting_blocks_by_custom_key_without_comment_preservation():
    bibtex = """
    % some comment
    @article{newer, year = {2020}}
    @article{older, year = {1999}}
    """

    def comments_last(block):
        if isinstance(block, Entry):
            return (0, int(block["year"]))
        return (1, 0)

    library = bibtexparser.parse_string(bibtex)
    library = SortBlocksMiddleware(key=comments_last, preserve_comments_on_top=False).transform(
        library
    )

    blocks = library.blocks
    assert isinstance(blocks[0], Entry) and blocks[0].key == "older"
    assert isinstance(blocks[1], Entry) and blocks[1].key == "newer"
    assert isinstance(blocks[2], ImplicitComment)
