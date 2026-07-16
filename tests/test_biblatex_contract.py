"""Compatibility contracts for BibLaTeX data sources processed by Biber.

BibLaTeX uses BibTeX-format data sources but defines a larger, configurable data
model and several Biber extensions. These tests deliberately exercise those
constructs separately from traditional BibTeX examples so compatibility cannot
regress under the misleading assumption that only the classic types and fields
matter.
"""

from pathlib import Path

from bibtexparser import parse_string
from bibtexparser import write_string

RESOURCE = Path(__file__).parent / "resources" / "biblatex_contract.bib"


def _entry_inventory(source: str) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """Return the ordered BibLaTeX information the structural codec must retain."""
    library = parse_string(source)
    assert library.failed_blocks == []
    return [
        (
            entry.entry_type,
            entry.key,
            [(field.key, field.value) for field in entry.fields],
        )
        for entry in library.entries
    ]


class TestBibLaTeXDataSourceContract:
    """Protect schema-agnostic parsing of the richer BibLaTeX data model."""

    def test_default_roundtrip_preserves_biblatex_extensions(self):
        """Default I/O retains types, fields, values, spelling, and source order."""
        source = RESOURCE.read_text(encoding="utf-8")

        written = write_string(parse_string(source))

        assert _entry_inventory(written) == _entry_inventory(source)

    def test_set_and_xdata_remain_first_class_entries(self):
        """Structural parsing must not discard inheritance or entry-set records."""
        library = parse_string(RESOURCE.read_text(encoding="utf-8"))

        assert library.entries_dict["shared-publisher"].entry_type == "XData"
        assert library.entries_dict["review-set"].entry_type == "Set"
        assert library.entries_dict["review-set"]["entryset"] == ("online-record,software-record")
        assert library.entries_dict["online-record"]["xdata"] == "shared-publisher"

    def test_annotations_and_extended_names_remain_uninterpreted(self):
        """Biber-only subgrammars stay lossless until explicitly interpreted."""
        entry = parse_string(RESOURCE.read_text(encoding="utf-8")).entries_dict["online-record"]

        assert entry["author"] == ("Family, Given and given=Sam, family=Researcher, prefix=von")
        assert entry["author+an"] == "1:family=lead;2=corresponding"
        assert entry["title+an:translation"] == '="An overview"'

    def test_custom_data_model_names_do_not_require_a_parser_option(self):
        """Unknown types and fields are data, not syntax errors for the codec."""
        source = (
            "@CustomEvidence{custom-record,"
            "customfield={A value permitted by a custom Biber data model}}"
        )
        entry = parse_string(source).entries_dict["custom-record"]

        assert entry.entry_type == "CustomEvidence"
        assert entry["customfield"] == ("A value permitted by a custom Biber data model")
