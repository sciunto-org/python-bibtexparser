import pytest

from bibtexparser.splitter import Splitter
from tests.resources import VALID_BIBTEX_SNIPPETS


@pytest.mark.parametrize("bibtex_before", VALID_BIBTEX_SNIPPETS)
@pytest.mark.parametrize(
    "faulty_block",
    [
        pytest.param(
            """@article{article1, title={title1}""", id="entry_without_closing_brace"
        ),
        pytest.param(
            """@article{article1, \n  title={title1}""",
            id="multiline_entry_without_closing_brace",
        ),
        pytest.param(
            """@article{article1,""", id="entry_without_field_and_closing_brace"
        ),
        pytest.param("""@article{article1""", id="entry_only_with_key_no_comma"),
        pytest.param(
            """@article{article1, title={title1} author={author1}""",
            id="entry_missing_comma_between_fields",
        ),
        pytest.param(
            """@article{article1, title={title1 author={author1}""",
            id="field_missing_closing_brace",
        ),
        pytest.param(
            """@article{article1, title="title1 author={author1}""",
            id="field_missing_closing_quote",
        ),
        pytest.param("""@string{foo = "bar""", id="string_without_closing_brace"),
        pytest.param("""@preamble{e = mc^2""", id="preable_without_closing_brace"),
        pytest.param("""@comment{foo = "bar""", id="preable_without_closing_brace"),
    ],
)
@pytest.mark.parametrize(
    "use_block_afterwards",
    [False, True],
    ids=["no_block_afterwards", "block_afterwards"],
)
def test_faulty_block_parsing(
    bibtex_before: str, faulty_block: str, use_block_afterwards: bool
):
    """Test that an unexpected block end raises a ParseError."""
    bibtex_str = f"{bibtex_before}\n{faulty_block}"
    if use_block_afterwards:
        bibtex_str += "\n@comment{This is a comment after a faulty block}"

    library = Splitter(bibtex_str).split()
    assert len(library.failed_blocks) == 1

    failed_block = library.failed_blocks[0]
    assert failed_block.start_line == bibtex_before.count("\n") + 1

    # Check that the following block (if present) is again parsed correctly.
    if use_block_afterwards:
        assert len(library.comments) >= 1
        assert (
            library.comments[-1].raw
            == "@comment{This is a comment after a faulty block}"
        )
        assert library.comments[-1].comment == "This is a comment after a faulty block"
        assert library.comments[-1].start_line == len(bibtex_str.splitlines()) - 1
