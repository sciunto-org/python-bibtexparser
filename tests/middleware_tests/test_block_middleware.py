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


class ConstantBlockMiddleware(BlockMiddleware):
    """A middleware that always returns the same result for every block."""

    def __init__(self, const):
        self._const = const
        super().__init__(allow_parallel_execution=True, allow_inplace_modification=True)

    def transform_block(self, block, library):
        return self._const

    def metadata_key():
        return "ConstantBlockMiddleware"


class LambdaBlockMiddleware(BlockMiddleware):
    """A middleware that applies a lambda to the input block"""

    def __init__(self, f):
        self._f = f
        super().__init__(allow_parallel_execution=True, allow_inplace_modification=True)

    def transform_block(self, block, library):
        return self._f(block)

    def metadata_key():
        return "LambdaBlockMiddleware"


@pytest.mark.parametrize(
    ("middleware", "expected"),
    [
        (ConstantBlockMiddleware(None), []),
        (ConstantBlockMiddleware([]), []),
        (LambdaBlockMiddleware(lambda b: [b]), BLOCKS),
    ],
)
def test_successful_transform(middleware, expected):
    library = Library(blocks=BLOCKS)
    library = middleware.transform(library)

    assert library.blocks == expected


def test_returning_list_adds_all():
    library = Library(blocks=BLOCKS)
    library = LambdaBlockMiddleware(
        lambda b: [ImplicitComment("% Block"), b]
    ).transform(library)

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


@pytest.mark.parametrize(
    "middleware",
    [
        ConstantBlockMiddleware(True),
        ConstantBlockMiddleware([True]),
        LambdaBlockMiddleware(
            lambda block: (b for b in [block])
        ),  # generators are not collections
    ],
)
def test_returning_invalid_raises_error(middleware):
    library = Library(blocks=BLOCKS)
    with pytest.raises(TypeError):
        middleware.transform(library)
