"""Tests the parsing of biber-style `%`-comments within entries (issue #372)."""

import pytest

from bibtexparser.splitter import Splitter


@pytest.mark.parametrize(
    "bibtex_str, expected_fields, expected_trailing_comments",
    [
        pytest.param(
            "@article{key,\n  %somecomment\n  author = {A},\n  title = {T},\n}",
            [("author", "{A}", ["somecomment"]), ("title", "{T}", [])],
            [],
            id="before_field",
        ),
        pytest.param(
            "@article{key,\n  author = {A},\n  %   title = {T},\n}",
            [("author", "{A}", [])],
            ["   title = {T},"],
            id="after_last_field",
        ),
        pytest.param(
            '@article{key,\n  % a, b = {c "d @misc{e,\n\n  % second\n  year = 2020\n}',
            [("year", "2020", [' a, b = {c "d @misc{e,', " second"])],
            [],
            id="syntax_in_comments",
        ),
        pytest.param(
            "@article{key,\n  author = {A}, % same line\n  year = 2020\n}",
            [("author", "{A}", []), ("year", "2020", [" same line"])],
            [],
            id="after_comma_on_same_line",
        ),
        pytest.param(
            "@article{key,\r\n  %c1\r\n  year = 2020,\r\n  %c2\r\n}",
            [("year", "2020", ["c1"])],
            ["c2"],
            id="crlf",
        ),
        pytest.param(
            "@article(key,\n  % (a)\n  year = 2020,\n  % b)\n)",
            [("year", "2020", [" (a)"])],
            [" b)"],
            id="parenthesis_block",
        ),
        pytest.param(
            "@article{key,\n  % no fields\n}",
            [],
            [" no fields"],
            id="no_fields",
        ),
    ],
)
def test_comments_within_entry(bibtex_str, expected_fields, expected_trailing_comments):
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    entry = library.entries[0]
    assert [(f.key, f.value, list(f.comments)) for f in entry.fields] == expected_fields
    assert list(entry.trailing_comments) == expected_trailing_comments


@pytest.mark.parametrize(
    "bibtex_str, expected_key, expected_value",
    [
        pytest.param("@misc{key, note = {a\n  % b}}", "key", "{a\n  % b}", id="curly"),
        pytest.param('@misc{key, note = "50% off"}', "key", '"50% off"', id="quotes"),
        pytest.param("@misc{50%off, note = {a}}", "50%off", "{a}", id="entry_key"),
    ],
)
def test_percent_outside_of_comment_position_is_literal(bibtex_str, expected_key, expected_value):
    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    entry = library.entries[0]
    assert entry.key == expected_key
    assert [(f.key, f.value, f.comments) for f in entry.fields] == [("note", expected_value, ())]


def test_comments_keep_line_numbers():
    # The `,` is a mark within the comment, which must be consumed while counting lines
    bibtex_str = "@article{key,\n  % a, b\n  % c\n  year = 2020,\n}\n\n@misc{other, title = {T}}"
    library = Splitter(bibtex_str).split()

    assert library.entries[0].fields[0].start_line == 3
    assert library.entries[1].start_line == 6
