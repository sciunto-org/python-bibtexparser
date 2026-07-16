"""Contracts separating permitted formatting cleanup from prohibited information loss.

The regular writer is allowed to normalize layout, line endings, optional
commas, and semantically equivalent value enclosures. It must not lose or
reorder meaningful blocks, comments, identifiers, fields, values, or retained
parse failures. Exact concrete-syntax preservation is a separate future mode.
"""

from typing import Any

from bibtexparser import parse_string
from bibtexparser import write_string
from bibtexparser.library import Library
from bibtexparser.model import Entry
from bibtexparser.model import ExplicitComment
from bibtexparser.model import ImplicitComment
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.model import Preamble
from bibtexparser.model import String


def _semantic_signature(library: Library) -> tuple[Any, ...]:
    """Return all source meaning that normal formatting must retain, in order."""
    signatures: list[tuple[Any, ...]] = []
    for block in library.blocks:
        if isinstance(block, Entry):
            fields = tuple((field.key, field.value) for field in block.fields)
            signatures.append(("entry", block.entry_type, block.key, fields))
        elif isinstance(block, String):
            signatures.append(("string", block.key, block.value))
        elif isinstance(block, Preamble):
            signatures.append(("preamble", block.value))
        elif isinstance(block, ExplicitComment):
            signatures.append(("explicit-comment", block.comment))
        elif isinstance(block, ImplicitComment):
            signatures.append(("implicit-comment", block.comment))
        elif isinstance(block, ParsingFailedBlock):
            signatures.append(("failed", block.raw))
        else:  # pragma: no cover - a new model type must extend the contract explicitly
            raise AssertionError(f"Unclassified block type: {type(block)}")
    return tuple(signatures)


def test_default_roundtrip_preserves_complete_semantic_inventory():
    """Formatting may change, but every meaningful block and value survives in order."""
    source = (
        "% Header retained\r\n"
        '@String { JournalMacro = "Journal of Tests" }\r\n'
        '@Preamble { "Prefix" }\r\n'
        "@Comment{An explicit comment}\r\n"
        '@Article{MixedKey, Year=2024, Title="A title", journal=JournalMacro,}\r\n'
        "@software{unsupported, title={Retained failure}"
    )
    parsed = parse_string(source)

    written = write_string(parsed)
    reparsed = parse_string(written)

    assert written != source
    assert _semantic_signature(reparsed) == _semantic_signature(parsed)


def test_default_roundtrip_preserves_block_and_field_order():
    """Canonical layout must not imply sorting unless sorting middleware was requested."""
    source = (
        "@misc{second, zeta={1}, Alpha={2}, middle={3}}\n"
        "@article{first, year={2024}, author={A}, title={T}}"
    )

    reparsed = parse_string(write_string(parse_string(source)))

    assert [entry.key for entry in reparsed.entries] == ["second", "first"]
    assert [field.key for field in reparsed.entries[0].fields] == [
        "zeta",
        "Alpha",
        "middle",
    ]
    assert [field.key for field in reparsed.entries[1].fields] == [
        "year",
        "author",
        "title",
    ]


def test_default_roundtrip_preserves_comment_content_and_position():
    """Comments are meaningful blocks; only surrounding separator whitespace may change."""
    source = (
        "Introductory prose\n"
        "@comment{Explicit first}\n"
        "Between entries\n"
        "@article{k, title={A}}\n"
        "% Closing comment"
    )
    parsed = parse_string(source)

    reparsed = parse_string(write_string(parsed))

    expected_comments = [(type(comment), comment.comment) for comment in parsed.comments]
    actual_comments = [(type(comment), comment.comment) for comment in reparsed.comments]
    assert actual_comments == expected_comments
    assert [type(block) for block in reparsed.blocks] == [type(block) for block in parsed.blocks]


def test_layout_cleanup_is_permitted_when_semantics_are_stable():
    """Line endings, indentation, spacing, trailing commas, and enclosures may normalize."""
    source = '@Article { Key ,\r\n  Title = "A title" ,\r\n\tyear=2024,\r\n}\r\n'
    parsed = parse_string(source)

    written = write_string(parsed)

    assert written != source
    assert "\r" not in written
    assert 'Title = "A title"' not in written
    assert "\tTitle = {A title}" in written
    assert _semantic_signature(parse_string(written)) == _semantic_signature(parsed)


def test_whitespace_only_input_may_normalize_to_empty_output():
    """Top-level whitespace without comments or blocks carries no bibliography meaning."""
    assert write_string(parse_string(" \t\r\n\r\n")) == ""


def test_model_edit_has_expected_semantics_without_affecting_other_records():
    """Edited and added fields serialize validly while unrelated record data remains stable."""
    source = (
        "@article{edited, author={A}, title={Original}, year={2024}}\n"
        "@misc{untouched, note={Keep me}, custom={And me}}"
    )
    library = parse_string(source)
    untouched_before = _semantic_signature(Library([library.entries[1]]))

    library.entries[0]["title"] = "Changed"
    library.entries[0]["doi"] = "10.0000/example"
    reparsed = parse_string(write_string(library))

    assert reparsed.entries[0]["title"] == "Changed"
    assert reparsed.entries[0]["doi"] == "10.0000/example"
    assert [field.key for field in reparsed.entries[0].fields] == [
        "author",
        "title",
        "year",
        "doi",
    ]
    assert _semantic_signature(Library([reparsed.entries[1]])) == untouched_before
