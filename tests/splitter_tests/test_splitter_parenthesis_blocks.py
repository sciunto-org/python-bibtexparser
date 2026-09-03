import pytest

import bibtexparser
from bibtexparser.model import Entry
from bibtexparser.model import ImplicitComment
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.splitter import Splitter

VALID_ENTRY = "@article{good2003, author = {B}, year = {2003}}"


def test_issue_533_repro():
    """Parenthesis-delimited entries must not be swallowed as implicit comments."""
    library = Splitter("@article(test2002, author = {A}, year = {2002})").split()

    assert len(library.entries) == 0
    assert len(library.comments) == 0
    assert len(library.failed_blocks) == 1

    failed_block = library.failed_blocks[0]
    assert failed_block.start_line == 0
    assert failed_block.raw == "@article(test2002, author = {A}, year = {2002})"
    assert "parenthes" in failed_block.error.abort_reason.lower()


@pytest.mark.parametrize(
    "block_type",
    ["article", "comment", "string", "preamble", "unknownblocktype"],
)
def test_all_block_types_with_parenthesis_fail(block_type: str):
    """All parenthesis-delimited blocks fail, regardless of their type."""
    library = Splitter(f"@{block_type}(foo = {{bar}})").split()

    assert len(library.blocks) == 1
    assert isinstance(library.blocks[0], ParsingFailedBlock)


@pytest.mark.parametrize(
    "spacing",
    ["", " ", "  ", "\t", " \t "],
    ids=["none", "space", "spaces", "tab", "mixed"],
)
def test_whitespace_between_type_and_parenthesis(spacing: str):
    """Whitespace before the `(` behaves like whitespace before a `{`."""
    library = Splitter(f"@article{spacing}(key, year = {{2002}})").split()

    assert len(library.blocks) == 1
    assert isinstance(library.blocks[0], ParsingFailedBlock)


@pytest.mark.parametrize(
    "paren_block",
    [
        pytest.param("@article(test2002, author = {A}, year = {2002})", id="single_line"),
        pytest.param("@article(test2002,\n  author = {A},\n  year = {2002})", id="multi_line"),
        pytest.param('@article(test2002, title = "a ) b")', id="parenthesis_in_quoted_value"),
        pytest.param("@article(test2002, title = {a ) b})", id="parenthesis_in_braced_value"),
        pytest.param("@article(test2002, title = {a (b) c})", id="nested_parenthesis_in_value"),
        pytest.param("@article(test2002)", id="key_only"),
        pytest.param("@article(broken", id="unclosed"),
    ],
)
def test_recovery_after_parenthesis_block(paren_block: str):
    """A parenthesis block must not prevent the following blocks from being parsed."""
    library = Splitter(f"{paren_block}\n{VALID_ENTRY}").split()

    assert len(library.failed_blocks) == 1
    assert len(library.entries) == 1

    entry = library.entries[0]
    assert entry.key == "good2003"
    assert entry.entry_type == "article"
    assert entry.fields_dict["author"].value == "{B}"
    assert entry.fields_dict["year"].value == "{2003}"
    assert entry.start_line == paren_block.count("\n") + 1


def test_parenthesis_block_between_valid_entries():
    """Blocks before and after a parenthesis block are unaffected."""
    bibtex_str = (
        "@article{before, year = {2001}}\n"
        "@article(broken2002, year = {2002})\n"
        "@article{after, year = {2003}}"
    )
    library = Splitter(bibtex_str).split()

    assert [type(block) for block in library.blocks] == [Entry, ParsingFailedBlock, Entry]
    assert [block.start_line for block in library.blocks] == [0, 1, 2]
    assert [entry.key for entry in library.entries] == ["before", "after"]


def test_implicit_comment_after_parenthesis_block_keeps_line_numbers():
    """Line numbers of subsequent blocks account for the skipped parenthesis block."""
    bibtex_str = "@article(broken,\n  year = {2002})\nsome implicit comment\n" + VALID_ENTRY
    library = Splitter(bibtex_str).split()

    assert [type(block) for block in library.blocks] == [
        ParsingFailedBlock,
        ImplicitComment,
        Entry,
    ]
    assert [block.start_line for block in library.blocks] == [0, 2, 3]
    assert library.comments[0].comment == "some implicit comment"


@pytest.mark.parametrize(
    "bibtex_str",
    [
        pytest.param("A comment mentioning (see below)", id="parenthesis_in_comment"),
        pytest.param("f(x) = y", id="function_call_in_comment"),
        pytest.param("@article{k, note = {see f(x) for details}}", id="parenthesis_in_value"),
        pytest.param('@article{k, note = "see f(x) for details"}', id="parenthesis_in_quoted"),
        pytest.param("@article{k, note = {@article (not a block)}}", id="at_in_value"),
    ],
)
def test_stray_parenthesis_is_inert(bibtex_str: str):
    """A `(` outside of a block-start position must not create a failed block."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0


def test_parenthesis_block_content_is_preserved():
    """The raw content of a parenthesis block is kept, so nothing is silently lost."""
    bibtex_str = "@article(test2002, author = {A}, year = {2002})"
    library = Splitter(bibtex_str).split()

    assert bibtex_str in bibtexparser.write_string(library)


@pytest.mark.parametrize(
    "bibtex_str",
    [
        pytest.param("@article{k, note = {a ( b}}", id="opening_parenthesis_in_value"),
        pytest.param("@article{k, note = {a ) b}}", id="closing_parenthesis_in_value"),
        pytest.param("@article{k, note = {f(x)}}", id="balanced_parentheses_in_value"),
    ],
)
def test_brace_delimited_entries_are_unaffected(bibtex_str: str):
    """Parentheses inside a `{`-delimited entry are plain characters."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert library.entries[0].raw == bibtex_str
