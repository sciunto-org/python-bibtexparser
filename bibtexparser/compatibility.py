"""Read-only compatibility checks for user-supplied bibliography data.

The checker exercises the public default parse/write path without changing the
source file. It verifies named invariants rather than claiming to prove that the
parser is correct for every possible input. In particular, reparsing with the
same implementation cannot independently validate every interpretation choice.
"""

from dataclasses import asdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .entrypoint import parse_string
from .entrypoint import write_string
from .library import Library
from .model import Entry
from .model import ExplicitComment
from .model import ImplicitComment
from .model import ParsingFailedBlock
from .model import Preamble
from .model import String


@dataclass(frozen=True)
class CompatibilityDiagnostic:
    """One actionable finding produced by a compatibility check."""

    code: str
    severity: str
    message: str
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class CompatibilityReport:
    """Results of exercising the default codec contract on one source."""

    source_sha256: str
    source_bytes: int
    source_lines: int | None
    block_count: int | None
    entry_count: int | None
    source_covered: bool | None
    parsed_without_failures: bool | None
    semantic_roundtrip: bool | None
    canonical_stable: bool | None
    output_encodable: bool | None
    exact_source_match: bool | None
    diagnostics: tuple[CompatibilityDiagnostic, ...]

    @property
    def compatible(self) -> bool:
        """Whether every required compatibility invariant passed."""
        required_checks = (
            self.source_covered,
            self.parsed_without_failures,
            self.semantic_roundtrip,
            self.canonical_stable,
            self.output_encodable,
        )
        return all(check is True for check in required_checks)

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation without source text."""
        return {
            "compatible": self.compatible,
            "source_sha256": self.source_sha256,
            "source_bytes": self.source_bytes,
            "source_lines": self.source_lines,
            "block_count": self.block_count,
            "entry_count": self.entry_count,
            "checks": {
                "source_covered": self.source_covered,
                "parsed_without_failures": self.parsed_without_failures,
                "semantic_roundtrip": self.semantic_roundtrip,
                "canonical_stable": self.canonical_stable,
                "output_encodable": self.output_encodable,
                "exact_source_match": self.exact_source_match,
            },
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def _library_signature(library: Library) -> tuple[Any, ...]:
    """Return ordered bibliography meaning protected by the default contract."""
    signatures: list[tuple[Any, ...]] = []
    for block in library.blocks:
        if isinstance(block, Entry):
            fields = tuple((field.key, field.value, field.enclosing) for field in block.fields)
            comments = tuple(
                (comment.comment, comment.field_index) for comment in getattr(block, "comments", ())
            )
            signatures.append(("entry", block.entry_type, block.key, fields, comments))
        elif isinstance(block, String):
            signatures.append(("string", block.key, block.value, block.enclosing))
        elif isinstance(block, Preamble):
            signatures.append(("preamble", block.value))
        elif isinstance(block, ExplicitComment):
            signatures.append(("explicit-comment", block.comment))
        elif isinstance(block, ImplicitComment):
            signatures.append(("implicit-comment", block.comment))
        elif isinstance(block, ParsingFailedBlock):
            signatures.append(("failed", block.raw, type(block.error).__name__))
        else:
            raise TypeError(f"Unsupported block type in compatibility check: {type(block)}")
    return tuple(signatures)


def _source_is_covered(source: str, library: Library) -> bool:
    """Check that block raw spans account for every non-whitespace source token."""
    cursor = 0
    for block in library.blocks:
        if block.raw is None:
            return False
        start = source.find(block.raw, cursor)
        if start < 0 or source[cursor:start].strip():
            return False
        cursor = start + len(block.raw)
    return not source[cursor:].strip()


def _failure_diagnostic(block: ParsingFailedBlock) -> CompatibilityDiagnostic:
    """Describe a failed block without copying bibliography contents."""
    line = block.start_line + 1 if block.start_line is not None else None
    return CompatibilityDiagnostic(
        code="parse-failure",
        severity="error",
        message=(
            f"{type(block).__name__} retained source that the parser could not "
            "represent as a normal block."
        ),
        line=line,
    )


def _check_source(
    source: str,
    source_bytes: bytes,
    output_encoding: str,
) -> CompatibilityReport:
    """Run the default compatibility checks for already decoded source."""
    diagnostics: list[CompatibilityDiagnostic] = []
    source_digest = sha256(source_bytes).hexdigest()

    try:
        library = parse_string(source)
    except Exception as error:
        diagnostics.append(
            CompatibilityDiagnostic(
                code="parse-error",
                severity="error",
                message=f"Parsing raised {type(error).__name__}.",
            )
        )
        return CompatibilityReport(
            source_sha256=source_digest,
            source_bytes=len(source_bytes),
            source_lines=len(source.splitlines()),
            block_count=None,
            entry_count=None,
            source_covered=None,
            parsed_without_failures=False,
            semantic_roundtrip=None,
            canonical_stable=None,
            output_encodable=None,
            exact_source_match=None,
            diagnostics=tuple(diagnostics),
        )

    source_covered = _source_is_covered(source, library)
    if not source_covered:
        diagnostics.append(
            CompatibilityDiagnostic(
                code="source-coverage-gap",
                severity="error",
                message="Parsed raw spans do not account for all non-whitespace source text.",
            )
        )

    for failed_block in library.failed_blocks:
        diagnostics.append(_failure_diagnostic(failed_block))
    parsed_without_failures = not library.failed_blocks

    if not parsed_without_failures:
        return CompatibilityReport(
            source_sha256=source_digest,
            source_bytes=len(source_bytes),
            source_lines=len(source.splitlines()),
            block_count=len(library.blocks),
            entry_count=len(library.entries),
            source_covered=source_covered,
            parsed_without_failures=False,
            semantic_roundtrip=None,
            canonical_stable=None,
            output_encodable=None,
            exact_source_match=None,
            diagnostics=tuple(diagnostics),
        )

    try:
        canonical = write_string(library)
        reparsed = parse_string(canonical)
        second_canonical = write_string(reparsed)
    except Exception as error:
        diagnostics.append(
            CompatibilityDiagnostic(
                code="roundtrip-error",
                severity="error",
                message=f"The default parse/write cycle raised {type(error).__name__}.",
            )
        )
        return CompatibilityReport(
            source_sha256=source_digest,
            source_bytes=len(source_bytes),
            source_lines=len(source.splitlines()),
            block_count=len(library.blocks),
            entry_count=len(library.entries),
            source_covered=source_covered,
            parsed_without_failures=parsed_without_failures,
            semantic_roundtrip=None,
            canonical_stable=None,
            output_encodable=None,
            exact_source_match=None,
            diagnostics=tuple(diagnostics),
        )

    if not library.failed_blocks and reparsed.failed_blocks:
        diagnostics.append(
            CompatibilityDiagnostic(
                code="reparse-failure",
                severity="error",
                message="Canonical output introduced one or more parse failures.",
            )
        )

    semantic_roundtrip = _library_signature(reparsed) == _library_signature(library)
    if not semantic_roundtrip:
        diagnostics.append(
            CompatibilityDiagnostic(
                code="semantic-roundtrip-mismatch",
                severity="error",
                message="Default writing and reparsing changed protected bibliography data.",
            )
        )

    canonical_stable = second_canonical == canonical
    if not canonical_stable:
        diagnostics.append(
            CompatibilityDiagnostic(
                code="unstable-canonical-output",
                severity="error",
                message="A second default parse/write cycle changed the output again.",
            )
        )

    try:
        canonical_bytes = canonical.encode(output_encoding)
    except (LookupError, UnicodeEncodeError) as error:
        output_encodable = False
        exact_source_match = None
        diagnostics.append(
            CompatibilityDiagnostic(
                code="encode-error",
                severity="error",
                message=(
                    f"Canonical output could not be encoded with {output_encoding!r}: "
                    f"{type(error).__name__}."
                ),
            )
        )
    else:
        output_encodable = True
        exact_source_match = canonical_bytes == source_bytes

    return CompatibilityReport(
        source_sha256=source_digest,
        source_bytes=len(source_bytes),
        source_lines=len(source.splitlines()),
        block_count=len(library.blocks),
        entry_count=len(library.entries),
        source_covered=source_covered,
        parsed_without_failures=parsed_without_failures,
        semantic_roundtrip=semantic_roundtrip,
        canonical_stable=canonical_stable,
        output_encodable=output_encodable,
        exact_source_match=exact_source_match,
        diagnostics=tuple(diagnostics),
    )


def check_string(source: str) -> CompatibilityReport:
    """Check whether a string passes the default non-lossy codec contract."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    return _check_source(source, source.encode("utf-8"), output_encoding="utf-8")


def check_file(path: str | Path, encoding: str = "UTF-8") -> CompatibilityReport:
    """Read a bibliography file without modifying it and check default compatibility.

    File-system errors are raised to the caller. Decoding failures are returned
    as incompatibility diagnostics because they describe the selected codec's
    compatibility with the supplied bytes.
    """
    source_bytes = Path(path).read_bytes()
    try:
        source = source_bytes.decode(encoding)
    except (LookupError, UnicodeDecodeError) as error:
        diagnostic = CompatibilityDiagnostic(
            code="decode-error",
            severity="error",
            message=f"The source could not be decoded with {encoding!r}: {type(error).__name__}.",
        )
        return CompatibilityReport(
            source_sha256=sha256(source_bytes).hexdigest(),
            source_bytes=len(source_bytes),
            source_lines=None,
            block_count=None,
            entry_count=None,
            source_covered=None,
            parsed_without_failures=None,
            semantic_roundtrip=None,
            canonical_stable=None,
            output_encodable=None,
            exact_source_match=None,
            diagnostics=(diagnostic,),
        )
    return _check_source(source, source_bytes, output_encoding=encoding)
