"""Behavioral contracts for explicit entry-type normalization."""

from bibtexparser import parse_string
from bibtexparser import write_string
from bibtexparser.middlewares import NormalizeEntryTypes


def test_entry_type_normalization_is_explicit():
    """Callers can request the lowercase behavior that source-preserving parsing replaced."""
    library = parse_string(
        "@Article{Mixed, title = {Case}}",
        append_middleware=[NormalizeEntryTypes()],
    )

    assert library.entries[0].entry_type == "article"
    assert write_string(library).startswith("@article{Mixed,")


def test_entry_type_normalization_can_avoid_mutating_input():
    """The standard middleware copy policy remains available for reusable libraries."""
    library = parse_string("@SoftwarePackage{Mixed, title = {Case}}")

    normalized = NormalizeEntryTypes(allow_inplace_modification=False).transform(library)

    assert library.entries[0].entry_type == "SoftwarePackage"
    assert normalized.entries[0].entry_type == "softwarepackage"
