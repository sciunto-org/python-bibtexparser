"""Blocks delimited by parentheses, e.g. `@article(...)`, which standard BibTeX allows."""

import pytest

import bibtexparser
from bibtexparser.model import Entry
from bibtexparser.model import ExplicitComment
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.model import Preamble
from bibtexparser.model import String
from bibtexparser.splitter import Splitter


def test_entry_with_parenthesis():
    """Issue #533: such entries used to be swallowed as implicit comments."""
    bibtex_str = "@article(test2002, author = {A}, year = {2002})"
    library = Splitter(bibtex_str).split()

    assert len(library.blocks) == 1
    entry = library.entries[0]
    assert entry.entry_type == "article"
    assert entry.key == "test2002"
    assert entry.fields_dict["author"].value == "{A}"
    assert entry.fields_dict["year"].value == "{2002}"
    assert entry.raw == bibtex_str


@pytest.mark.parametrize(
    "spacing",
    ["", " ", "\t", " \t "],
    ids=["none", "space", "tab", "mixed"],
)
def test_whitespace_between_type_and_parenthesis(spacing: str):
    library = Splitter(f"@article{spacing}(key, year = {{2002}})").split()

    assert len(library.blocks) == 1
    assert library.entries[0].key == "key"


def test_entry_without_fields():
    library = Splitter("@article(onlykey)").split()

    assert len(library.blocks) == 1
    assert library.entries[0].key == "onlykey"
    assert library.entries[0].fields == []


@pytest.mark.parametrize(
    ("bibtex_str", "expected_value"),
    [
        pytest.param('@article(k, title = "a ) b")', '"a ) b"', id="quoted"),
        pytest.param("@article(k, title = {a ) b})", "{a ) b}", id="braced"),
        pytest.param("@article(k, title = {a (b) c})", "{a (b) c}", id="nested"),
        pytest.param("@article(k, title = {a {( b} c})", "{a {( b} c}", id="nested_braces"),
    ],
)
def test_parenthesis_in_field_value_does_not_close_entry(bibtex_str: str, expected_value: str):
    library = Splitter(bibtex_str).split()

    assert len(library.blocks) == 1
    assert library.entries[0].fields_dict["title"].value == expected_value
    assert library.entries[0].raw == bibtex_str


@pytest.mark.parametrize("delimiters", ["{}", "()"])
def test_at_sign_followed_by_brace_within_value(delimiters: str):
    """Regression: an `@word {` within a value must not be mistaken for a block start,
    nor must its `{` be lost for brace counting (cf. issue #488)."""
    opening, closing = delimiters
    bibtex_str = (
        f"@article{opening}k,\n"
        "  title = {LeQua @ {CLEF} 2022: {A} Shared Task},\n"
        "  note = {see @foo{bar} and @baz(qux)},\n"
        "  year = {2021}\n"
        f"{closing}"
    )
    library = Splitter(bibtex_str).split()

    assert len(library.blocks) == 1
    entry = library.entries[0]
    assert entry.fields_dict["title"].value == "{LeQua @ {CLEF} 2022: {A} Shared Task}"
    assert entry.fields_dict["note"].value == "{see @foo{bar} and @baz(qux)}"
    assert entry.fields_dict["year"].value == "{2021}"
    assert entry.raw == bibtex_str


@pytest.mark.parametrize(
    ("bibtex_str", "expected_value"),
    [
        pytest.param('@string(s = "a ) b")', '"a ) b"', id="string"),
        pytest.param('@string(s = "a {"} b")', '"a {"} b"', id="string_escaped_quote"),
        pytest.param('@preamble(")" # foo)', '")" # foo', id="preamble"),
    ],
)
def test_parenthesis_in_quoted_string_or_preamble_value(bibtex_str: str, expected_value: str):
    library = Splitter(bibtex_str).split()

    assert len(library.blocks) == 1
    assert library.blocks[0].value == expected_value
    assert library.blocks[0].raw == bibtex_str


def test_string_preamble_and_comment_with_parenthesis():
    bibtex_str = (
        '@string(foo = "bar")\n'
        '@preamble( "\\newcommand{\\x}{y}" # foo )\n'
        '@comment(some {braced} "unbalanced comment)'
    )
    library = Splitter(bibtex_str).split()

    assert [type(block) for block in library.blocks] == [String, Preamble, ExplicitComment]
    assert library.strings[0].key == "foo"
    assert library.strings[0].value == '"bar"'
    assert library.preambles[0].value.strip() == '"\\newcommand{\\x}{y}" # foo'
    assert library.comments[0].comment == 'some {braced} "unbalanced comment'
    assert [block.start_line for block in library.blocks] == [0, 1, 2]


def test_mixed_delimiters_in_one_file():
    bibtex_str = (
        "@article{curly, year = {2001}}\n"
        "@article(round, year = {2002})\n"
        "some implicit comment\n"
        "@article{curly2, year = {2003}}\n"
        "@article(round2,\n  year = {2004}\n)"
    )
    library = Splitter(bibtex_str).split()

    assert [entry.key for entry in library.entries] == ["curly", "round", "curly2", "round2"]
    assert [entry.start_line for entry in library.entries] == [0, 1, 3, 4]
    assert len(library.comments) == 1
    assert library.comments[0].start_line == 2
    assert len(library.failed_blocks) == 0


@pytest.mark.parametrize(
    "broken_block",
    [
        pytest.param("@article(broken,\n  year = {2002},\n", id="new_block_while_expecting_key"),
        pytest.param("@article(broken,\n  year = {2002\n", id="new_block_within_value"),
        pytest.param("@article(broken,\n  year = {2002}\n", id="new_block_while_expecting_comma"),
        pytest.param("@article(broken\n", id="new_block_while_expecting_key_comma"),
        pytest.param("@string(broken\n", id="new_block_in_string"),
        pytest.param("@comment(broken\n", id="new_block_in_comment"),
        pytest.param("@article(broken, year = {2002}}\n", id="curly_instead_of_parenthesis"),
    ],
)
@pytest.mark.parametrize("next_delimiter", ["{", "("])
def test_recovery_after_broken_parenthesis_block(broken_block: str, next_delimiter: str):
    """After a failed `(`-block, the next block is parsed normally, whatever its delimiter."""
    closing = "}" if next_delimiter == "{" else ")"
    next_block = f"@article{next_delimiter}good, year = {{2003}}{closing}"
    library = Splitter(broken_block + next_block).split()

    assert [type(block) for block in library.blocks] == [ParsingFailedBlock, Entry]
    assert library.failed_blocks[0].start_line == 0
    assert library.failed_blocks[0].raw.startswith(broken_block.rstrip())
    assert library.entries[0].key == "good"
    assert library.entries[0].fields_dict["year"].value == "{2003}"
    assert library.entries[0].start_line == broken_block.count("\n")


@pytest.mark.parametrize("delimiters", ["{}", "()"])
def test_recovery_from_unclosed_block_at_parenthesis_block(delimiters: str):
    """Like for `@type{`, an `@type(` at line start ends an unclosed preceding block."""
    opening, closing = delimiters
    bibtex_str = f"@article{opening}broken, year = {{2002\n@article(good, year = {{2003}})"
    library = Splitter(bibtex_str).split()

    assert [type(block) for block in library.blocks] == [ParsingFailedBlock, Entry]
    assert library.entries[0].key == "good"
    assert library.entries[0].start_line == 1


def test_unclosed_parenthesis_block_at_eof():
    library = Splitter("@article(broken, year = {2002}").split()

    assert [type(block) for block in library.blocks] == [ParsingFailedBlock]


@pytest.mark.parametrize(
    "bibtex_str",
    [
        pytest.param("@article{k(1), note = {f(x)}}", id="parenthesis_in_key_and_value"),
        pytest.param("@article{k, note = a ) b}", id="unenclosed_closing_parenthesis"),
        pytest.param('@article{k, note = "( unbalanced"}', id="unbalanced_in_quotes"),
    ],
)
def test_parenthesis_in_curly_block_is_plain_text(bibtex_str: str):
    library = Splitter(bibtex_str).split()

    assert len(library.blocks) == 1
    assert library.entries[0].raw == bibtex_str


def test_parse_and_write_roundtrip():
    """End-to-end: default middlewares apply, and the entry is written back (with braces)."""
    library = bibtexparser.parse_string(
        "@article(test2002,\n  author = {Doe, John},\n  year = 2002\n)"
    )

    assert len(library.failed_blocks) == 0
    entry = library.entries[0]
    assert entry.fields_dict["author"].value == "Doe, John"
    assert entry.fields_dict["year"].value == "2002"

    written = bibtexparser.write_string(library)
    assert "@article{test2002," in written
    assert bibtexparser.parse_string(written).entries[0].key == "test2002"
