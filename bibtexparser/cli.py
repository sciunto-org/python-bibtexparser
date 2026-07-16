"""Command-line interface for explicit bibliography compatibility checks."""

import argparse
import json
import sys
from collections.abc import Sequence
from hashlib import sha256
from pathlib import Path

from . import __version__
from .compatibility import CompatibilityReport
from .compatibility import build_issue_url
from .compatibility import check_file
from .compatibility import extract_reproduction_snippet


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bibtexparser")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser(
        "check",
        help="exercise the default non-lossy contract without modifying the file",
    )
    check_parser.add_argument("file", type=Path, help="BibTeX or BibLaTeX file to check")
    check_parser.add_argument(
        "--encoding",
        default="UTF-8",
        help="source encoding (default: UTF-8)",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable report",
    )
    issue_link_group = check_parser.add_mutually_exclusive_group()
    issue_link_group.add_argument(
        "--no-issue-link",
        action="store_true",
        help="do not include a pre-filled GitHub issue form URL on failure",
    )
    issue_link_group.add_argument(
        "--include-source-in-issue-link",
        action="store_true",
        help=(
            "also generate a sensitive issue URL containing an exact failed block "
            "when a bounded reproduction can be extracted"
        ),
    )
    return parser


def _check_label(value: bool | None) -> str:
    if value is None:
        return "not run"
    return "passed" if value else "failed"


def _identity_label(value: bool | None) -> str:
    if value is None:
        return "not run"
    return "unchanged" if value else "would change"


def _print_text_report(
    report: CompatibilityReport,
    issue_url: str | None,
    reproduction_issue_url: str | None,
    reproduction_notice: str | None,
) -> None:
    status = "COMPATIBLE" if report.compatible else "INCOMPATIBLE"
    print(f"{status}: default bibliography codec checks")
    print(f"  Source coverage: {_check_label(report.source_covered)}")
    print(f"  Parse failures absent: {_check_label(report.parsed_without_failures)}")
    print(f"  Semantic round trip: {_check_label(report.semantic_roundtrip)}")
    print(f"  Canonical output stable: {_check_label(report.canonical_stable)}")
    print(f"  Output encodable: {_check_label(report.output_encodable)}")
    print(f"  Exact source bytes: {_identity_label(report.exact_source_match)}")
    if report.exact_source_match is False and report.compatible:
        print("  Note: default writing would normalize layout, but protected data is stable.")

    for diagnostic in report.diagnostics:
        location = f" line {diagnostic.line}" if diagnostic.line is not None else ""
        print(
            f"  {diagnostic.severity.upper()} [{diagnostic.code}]{location}: "
            f"{diagnostic.message}"
        )

    if issue_url is not None:
        print("  The link below opens a reviewable draft; it does not create an issue.")
        print("  It contains no file path, bibliography content, or source snippet.")
        print(f"  Privacy-safe issue draft: {issue_url}")
        if reproduction_issue_url is None:
            print(
                "  To request a second draft containing an exact failed block, rerun with "
                "--include-source-in-issue-link."
            )
            print(
                "  Warning: that URL exposes source in terminal logs, browser history, "
                "and the GitHub draft."
            )
    if reproduction_notice is not None:
        print(f"  Source-bearing draft unavailable: {reproduction_notice}")
    if reproduction_issue_url is not None:
        print(
            "  WARNING: the next URL contains bibliography source and may persist in "
            "terminal logs and browser history."
        )
        print("  Review the URL and GitHub draft carefully before submitting anything.")
        print(f"  Issue draft with reproduction: {reproduction_issue_url}")


def _run_check(args: argparse.Namespace) -> int:
    try:
        report = check_file(args.file, encoding=args.encoding)
    except OSError as error:
        print(f"Could not read {args.file}: {error}", file=sys.stderr)
        return 2

    issue_url = None
    reproduction_issue_url = None
    reproduction_notice = None
    if not report.compatible and not args.no_issue_link:
        issue_url = build_issue_url(report)
        if args.include_source_in_issue_link:
            try:
                source_bytes = args.file.read_bytes()
                if sha256(source_bytes).hexdigest() != report.source_sha256:
                    reproduction_notice = (
                        "the file changed after the compatibility check; rerun the command"
                    )
                else:
                    source = source_bytes.decode(args.encoding)
                    reproduction = extract_reproduction_snippet(source)
                    if reproduction is None:
                        reproduction_notice = (
                            "no exact bounded failed-block reproduction could be "
                            "extracted; add a reviewed minimal example manually"
                        )
                    else:
                        reproduction_issue_url = build_issue_url(
                            report,
                            reproduction=reproduction,
                        )
            except OSError:
                reproduction_notice = "the file could not be reread for a source-bearing draft"
            except (LookupError, UnicodeDecodeError):
                reproduction_notice = "the selected encoding could not decode the source"
            except ValueError as error:
                reproduction_notice = str(error)

    if args.json:
        serialized = report.to_dict()
        serialized["issue_url"] = issue_url
        serialized["reproduction_issue_url"] = reproduction_issue_url
        serialized["reproduction_notice"] = reproduction_notice
        print(json.dumps(serialized, indent=2, sort_keys=True))
    else:
        _print_text_report(
            report,
            issue_url,
            reproduction_issue_url,
            reproduction_notice,
        )
    return 0 if report.compatible else 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return its process exit status."""
    args = _parser().parse_args(argv)
    if args.command == "check":
        return _run_check(args)
    raise AssertionError(f"Unhandled command: {args.command}")
