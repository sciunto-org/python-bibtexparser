"""Tests that the mark tokenizer treats backslash runs by parity.

A backslash escapes the character right after it, so a backslash which is itself
escaped cannot escape the next one. Only an odd-length run hides the delimiter
behind it; an even-length run leaves it in force.
"""

import pytest as pytest

import bibtexparser
from bibtexparser.library import Library
from bibtexparser.model import Entry
from bibtexparser.model import Field
from bibtexparser.splitter import Splitter

BS = "\\"

EVEN_RUNS = [0, 2, 4]
ODD_RUNS = [1, 3]

# Value shapes, each with a `%s` slot for the backslash run right before the
# delimiter that ends (or is contained in) the value.
CLOSED_VALUES = {"braced": "{v%s}", "quoted": '"v%s"'}
OPEN_VALUES = {"bare": "v%s", "nested-group": "{a%s{b} c}"}
ALL_VALUES = {**CLOSED_VALUES, **OPEN_VALUES}


def _parse_entry(value: str) -> Library:
    return Splitter("@article{key,\n    title = " + value + ",\n    year = {2024}\n}").split()


@pytest.mark.parametrize("run", EVEN_RUNS)
@pytest.mark.parametrize("template", ALL_VALUES.values(), ids=ALL_VALUES.keys())
def test_even_backslash_run_leaves_delimiter_in_force(template: str, run: int):
    value = template % (BS * run)
    library = _parse_entry(value)

    assert library.failed_blocks == []
    fields = library.entries[0].fields_dict
    assert set(fields) == {"title", "year"}
    assert fields["title"].value == value
    assert fields["year"].value == "{2024}"


@pytest.mark.parametrize("run", ODD_RUNS)
@pytest.mark.parametrize("template", CLOSED_VALUES.values(), ids=CLOSED_VALUES.keys())
def test_odd_backslash_run_escapes_the_closing_enclosing(template: str, run: int):
    """The value is never closed, so the block is reported as failed."""
    library = _parse_entry(template % (BS * run))

    assert len(library.failed_blocks) == 1
    assert library.entries == []


@pytest.mark.parametrize("run", ODD_RUNS)
@pytest.mark.parametrize("template", OPEN_VALUES.values(), ids=OPEN_VALUES.keys())
def test_odd_backslash_run_escapes_the_field_separator(template: str, run: int):
    """The following comma is escaped, so the rest of the entry is part of the value."""
    library = _parse_entry(template % (BS * run))

    assert library.failed_blocks == []
    assert set(library.entries[0].fields_dict) == {"title"}


@pytest.mark.parametrize("run", EVEN_RUNS)
def test_even_backslash_run_closes_string_block(run: int):
    library = Splitter("@string{s = {v" + BS * run + "}}").split()

    assert library.failed_blocks == []
    assert library.strings[0].value == "{v" + BS * run + "}"


@pytest.mark.parametrize("run", EVEN_RUNS)
def test_even_backslash_run_closes_preamble_block(run: int):
    library = Splitter("@preamble{{v" + BS * run + "}}").split()

    assert library.failed_blocks == []
    assert library.preambles[0].value == "{v" + BS * run + "}"


@pytest.mark.parametrize("run", EVEN_RUNS)
def test_even_backslash_run_closes_explicit_comment_block(run: int):
    library = Splitter("@comment{c" + BS * run + "}\n@article{key, year = {2024}}").split()

    assert library.failed_blocks == []
    assert library.comments[0].comment == "c" + BS * run
    assert library.entries[0].key == "key"


@pytest.mark.parametrize("run", ODD_RUNS + EVEN_RUNS)
def test_backslashes_at_end_of_line_do_not_shift_line_numbers(run: int):
    """A LaTeX line break (`\\\\`) at the end of a line is not a line continuation."""
    bibtex = (
        "@article{first,\n"
        "    abstract = {First line." + BS * run + "\n"
        "                Second line.},\n"
        "    year = {2024}\n"
        "}\n"
        "\n"
        "@book{second,\n"
        "    year = {1999}\n"
        "}"
    )

    library = Splitter(bibtex).split()

    assert [block.start_line for block in library.blocks] == [0, 6]
    assert library.entries[0].fields_dict["year"].start_line == 3


@pytest.mark.parametrize("run", EVEN_RUNS)
def test_written_backslash_run_is_read_back_unchanged(run: int):
    """The writer emits these values, so the splitter has to accept them again."""
    value = "C:" + BS * run
    library = Library()
    library.add(Entry("article", "key", [Field("title", value), Field("year", "2024")]))

    reparsed = bibtexparser.parse_string(bibtexparser.write_string(library))

    assert reparsed.failed_blocks == []
    assert reparsed.entries[0].fields_dict["title"].value == value
    assert reparsed.entries[0].fields_dict["year"].value == "2024"


def test_escaped_delimiter_in_an_entry_key_is_not_a_mark():
    library = Splitter("@article{ke" + BS + "{y, title = {v}}").split()

    assert library.failed_blocks == []
    assert library.entries[0].key == "ke" + BS + "{y"
    assert library.entries[0].fields_dict["title"].value == "{v}"


def test_escaped_delimiter_in_a_field_key_is_not_a_mark():
    library = Splitter("@article{key, ti" + BS + "=tle = {v}, year = {2024}}").split()

    assert library.failed_blocks == []
    assert set(library.entries[0].fields_dict) == {"ti" + BS + "=tle", "year"}


def test_escaped_delimiter_in_a_string_key_is_not_a_mark():
    library = Splitter("@string{s" + BS + "{x = {v}}").split()

    assert library.failed_blocks == []
    assert library.strings[0].key == "s" + BS + "{x"
