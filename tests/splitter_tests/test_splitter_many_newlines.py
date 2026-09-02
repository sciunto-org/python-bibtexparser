"""Tests for bibtex containing long runs of consecutive newlines.

Skipping newlines used to be implemented recursively, which raised a
`RecursionError` on files containing roughly 1000 or more consecutive lines
without any of the characters `{`, `}`, `"`, `,` or `=`."""

import bibtexparser
from bibtexparser.splitter import Splitter

MANY = 3000


def test_many_blank_lines_between_blocks():
    """Long runs of blank lines between blocks must not abort parsing."""
    bibtex_str = (
        "@article{article1, title={title1}}" + "\n" * MANY + "@article{article2, title={title2}}"
    )

    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert [entry.key for entry in library.entries] == ["article1", "article2"]


def test_many_newlines_in_braced_field_value():
    """Long runs of newlines within a braced field value must not abort parsing."""
    bibtex_str = "@article{article1, title={before" + "\n" * MANY + "after}}"

    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert library.entries[0].fields_dict["title"].value == "{before" + "\n" * MANY + "after}"


def test_many_newlines_in_quoted_field_value():
    """Long runs of newlines within a quoted field value must not abort parsing."""
    bibtex_str = '@article{article1, title="before' + "\n" * MANY + 'after"}'

    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert library.entries[0].fields_dict["title"].value == '"before' + "\n" * MANY + 'after"'


def test_line_numbers_after_many_blank_lines():
    """Line numbers must remain correct after a large run of blank lines."""
    bibtex_str = "\n" * MANY + "@article{article1,\n    title={title1},\n    year={2020}\n}"

    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    entry = library.entries[0]
    assert entry.start_line == MANY
    assert entry.fields_dict["title"].start_line == MANY + 1
    assert entry.fields_dict["year"].start_line == MANY + 2


def test_many_blank_lines_in_implicit_comment():
    """Long runs of blank lines around an implicit comment must not abort parsing."""
    bibtex_str = (
        "An implicit comment."
        + "\n" * MANY
        + "Another implicit comment.\n"
        + "@article{article1, title={title1}}"
    )

    library = Splitter(bibtex_str).split()

    assert len(library.failed_blocks) == 0
    assert len(library.entries) == 1
    assert library.entries[0].start_line == MANY + 1
    assert [comment.comment for comment in library.comments] == [
        "An implicit comment." + "\n" * MANY + "Another implicit comment."
    ]


def test_many_blank_lines_at_end_of_file():
    """A file ending in many blank lines must not abort parsing."""
    bibtex_str = "@article{article1, title={title1}}" + "\n" * MANY

    library = bibtexparser.parse_string(bibtex_str)

    assert len(library.failed_blocks) == 0
    assert [entry.key for entry in library.entries] == ["article1"]
