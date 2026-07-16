"""Command-line contracts for read-only compatibility checks."""

import json
import os
import tempfile
from pathlib import Path
from urllib.parse import parse_qs
from urllib.parse import urlparse

from bibtexparser.cli import main


class TestCompatibilityCheckCli:
    """Protect exit statuses, useful output, and issue-report privacy."""

    def _source_file(self, source: str) -> Path:
        file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix="-private.bib",
            encoding="utf-8",
            delete=False,
        )
        with file:
            file.write(source)
        return Path(file.name)

    def test_supported_file_exits_successfully_without_issue_link(self, capsys):
        """A passing preflight explains allowed formatting changes without alarm."""
        path = self._source_file("@article{k, title={Supported}}")
        try:
            status = main(["check", str(path)])
            output = capsys.readouterr().out
        finally:
            os.unlink(path)

        assert status == 0
        assert output.startswith("COMPATIBLE:")
        assert "would normalize layout" in output
        assert "github.com" not in output

    def test_failure_offers_reviewable_privacy_safe_issue_draft(self, capsys):
        """The issue URL contains diagnostics but no path, snippet, or submission action."""
        source = "@article{private-record, title={Secret title}"
        path = self._source_file(source)
        try:
            status = main(["check", str(path)])
            output = capsys.readouterr().out
        finally:
            os.unlink(path)

        issue_url = next(
            line.removeprefix("  Report issue: ")
            for line in output.splitlines()
            if line.startswith("  Report issue: ")
        )
        query = parse_qs(urlparse(issue_url).query)
        issue_body = query["body"][0]

        assert status == 1
        assert "opens a reviewable draft; it does not create an issue" in output
        assert "parse-failure" in query["title"][0]
        assert "parse-failure" in issue_body
        assert str(path) not in issue_body
        assert path.name not in issue_body
        assert source not in issue_body
        assert "Secret title" not in issue_body
        assert "No file path, bibliography content, or source snippet" in issue_body

    def test_json_report_can_omit_issue_link(self, capsys):
        """Applications receive stable structured output and can suppress the URL."""
        path = self._source_file("@article{private-record, title={Secret title}")
        try:
            status = main(["check", str(path), "--json", "--no-issue-link"])
            captured = capsys.readouterr()
        finally:
            os.unlink(path)

        report = json.loads(captured.out)
        assert status == 1
        assert report["compatible"] is False
        assert report["issue_url"] is None
        assert report["diagnostics"][0]["code"] == "parse-failure"

    def test_missing_file_is_a_usage_error(self, capsys):
        """I/O failures are distinct from an incompatible bibliography result."""
        status = main(["check", "does-not-exist.bib"])
        captured = capsys.readouterr()

        assert status == 2
        assert captured.out == ""
        assert "Could not read" in captured.err
