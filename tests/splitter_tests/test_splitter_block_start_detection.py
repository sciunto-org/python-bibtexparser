"""Tests for block start detection behavior.

These tests verify the fix for issue #488 and the tradeoffs discussed in PR #416:
- @ signs in field values should not be treated as new block starts
- Multiple blocks on the same line should be parsed correctly
- Error recovery should still work when a new block starts at line start
"""

from textwrap import dedent

import pytest

from bibtexparser.splitter import Splitter

# =============================================================================
# Test: @ signs in field values (issue #488)
# =============================================================================


@pytest.mark.parametrize(
    "bibtex_str,expected_key,expected_field,expected_substring",
    [
        pytest.param(
            dedent(
                """\
                @inproceedings{DBLP:conf/cikm/EsuliM021,
                  author = {Andrea Esuli},
                  title = {LeQua @ {CLEF} 2022: {A} Shared Task},
                  year = {2021}
                }"""
            ),
            "DBLP:conf/cikm/EsuliM021",
            "title",
            "@ {CLEF}",
            id="at_sign_space_brace_in_title",
        ),
        pytest.param(
            "@article{test, email = {john.doe@example.com}}",
            "test",
            "email",
            "john.doe@example.com",
            id="email_address_in_braces",
        ),
        pytest.param(
            '@article{test, email = "john.doe@example.com"}',
            "test",
            "email",
            "john.doe@example.com",
            id="email_address_in_quotes",
        ),
        pytest.param(
            "@article{test, note = {Contact alice@a.com or bob@b.com}}",
            "test",
            "note",
            "alice@a.com",
            id="multiple_at_signs",
        ),
        pytest.param(
            "@article{test, title = {Workshop @ {ICML} 2023}}",
            "test",
            "title",
            "@ {ICML}",
            id="at_sign_followed_by_brace",
        ),
        pytest.param(
            '@article{test, title = "BibTeX entries start with @article{"}',
            "test",
            "title",
            "@article{",
            id="literal_at_entry_in_quotes",
        ),
        pytest.param(
            # Note: 3 closing braces - inner {}, title field, entry
            "@article{test, title = {BibTeX entries start with @article{}}}",
            "test",
            "title",
            "@article{",
            id="literal_at_entry_in_braces",
        ),
    ],
)
def test_at_sign_in_field_value(
    bibtex_str: str, expected_key: str, expected_field: str, expected_substring: str
):
    """@ signs in field values should be parsed as content, not block starts."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert library.entries[0].key == expected_key
    assert expected_substring in library.entries[0][expected_field]


# =============================================================================
# Test: Multiple blocks on the same line
# =============================================================================


@pytest.mark.parametrize(
    "bibtex_str,expected_entry_keys",
    [
        pytest.param(
            "@article{key1, title={A}} @book{key2, title={B}}",
            ["key1", "key2"],
            id="two_entries_with_space",
        ),
        pytest.param(
            "@article{key1,title={A}}@book{key2,title={B}}",
            ["key1", "key2"],
            id="two_entries_no_space",
        ),
        pytest.param(
            "@article{a, x={1}} @book{b, y={2}} @misc{c, z={3}}",
            ["a", "b", "c"],
            id="three_entries",
        ),
    ],
)
def test_multiple_entries_same_line(bibtex_str: str, expected_entry_keys: list):
    """Multiple well-formed entries on the same line should all be parsed."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == len(expected_entry_keys)
    assert [e.key for e in library.entries] == expected_entry_keys


@pytest.mark.parametrize(
    "bibtex_str,expected_entries,expected_strings,expected_comments",
    [
        pytest.param(
            '@article{key1, title={A}} @string{mystr = "value"}',
            1,
            1,
            0,
            id="entry_and_string",
        ),
        pytest.param(
            "@article{key1, title={A}} @comment{A comment}",
            1,
            0,
            1,
            id="entry_and_comment",
        ),
    ],
)
def test_mixed_blocks_same_line(
    bibtex_str: str, expected_entries: int, expected_strings: int, expected_comments: int
):
    """Different block types on the same line should all be parsed."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == expected_entries
    assert len(library.strings) == expected_strings
    assert len(library.comments) == expected_comments


# =============================================================================
# Test: Error recovery when new block starts at line start
# =============================================================================


@pytest.mark.parametrize(
    "bibtex_str,expected_valid_key",
    [
        pytest.param(
            dedent(
                """\
                @article{broken, title={Unclosed
                @article{valid, title={Valid Entry}}"""
            ),
            "valid",
            id="unclosed_entry_field",
        ),
        pytest.param(
            dedent(
                """\
                @string{broken = {unclosed value
                @article{valid, title={Valid Entry}}"""
            ),
            "valid",
            id="unclosed_string",
        ),
        pytest.param(
            dedent(
                """\
                @article{broken, title={Unclosed
                    @article{valid, title={Valid Entry}}"""
            ),
            "valid",
            id="indented_new_block",
        ),
    ],
)
def test_error_recovery_at_line_start(bibtex_str: str, expected_valid_key: str):
    """New block at line start should trigger recovery from malformed block."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 1
    assert len(library.entries) == 1
    assert library.entries[0].key == expected_valid_key


def test_error_recovery_preserves_failed_block_raw():
    """The failed block should contain raw text up to where recovery started."""
    bibtex_str = dedent(
        """\
        @article{broken, title={This is unclosed
        @article{valid, title={OK}}"""
    )
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 1
    failed = library.failed_blocks[0]
    assert "broken" in failed.raw
    assert "This is unclosed" in failed.raw


# =============================================================================
# Test: No false recovery for @ mid-line
# =============================================================================


@pytest.mark.parametrize(
    "bibtex_str",
    [
        pytest.param(
            "@article{test, title={unclosed @misc{fake}",
            id="at_entry_mid_line",
        ),
        pytest.param(
            "@article{test, title={text @ {more} unclosed",
            id="at_brace_mid_line",
        ),
    ],
)
def test_no_false_recovery_mid_line(bibtex_str: str):
    """@ mid-line should not trigger false error recovery."""
    library = Splitter(bibtex_str).split()

    # Should fail as one block, no recovery
    assert len(library.failed_blocks) == 1
    assert len(library.entries) == 0


# =============================================================================
# Test: Edge cases
# =============================================================================


@pytest.mark.parametrize(
    "bibtex_str",
    [
        pytest.param(
            "@article{test, title={Hello}}",
            id="block_at_file_start",
        ),
        pytest.param(
            "   \t  @article{test, title={Hello}}",
            id="block_after_whitespace_only",
        ),
        pytest.param(
            "@article{test, title={L1 {L2 {user@email.com} back} done}}",
            id="nested_braces_with_at",
        ),
    ],
)
def test_edge_cases_entries(bibtex_str: str):
    """Various edge cases should parse without failure."""
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1


def test_preamble_with_at_sign():
    """@ sign inside a preamble block."""
    bibtex_str = '@preamble{"Contact: admin@site.org"}'
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.preambles) == 1


def test_explicit_comment_with_at_sign():
    """@ sign inside an explicit comment block."""
    bibtex_str = "@comment{Email: test@example.com}"
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.comments) == 1
    assert "test@example.com" in library.comments[0].comment
