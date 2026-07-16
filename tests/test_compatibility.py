"""Public compatibility checks for user-supplied bibliography files."""

import os
import tempfile

import bibtexparser.compatibility as compatibility
from bibtexparser import check_file
from bibtexparser import check_string


class TestCompatibilityReport:
    """Protect each invariant behind the user-facing compatibility result."""

    def test_rich_supported_source_passes_all_required_checks(self):
        """A rich supported source reports preservation and expected reformatting."""
        source = (
            "% Synthetic header\n"
            '@string{journalName="Journal of Tests"}\n'
            "@online{record, title={A UTF-8 Überblick}, journal=journalName, "
            "date={2024-03/2024-05}}"
        )

        report = check_string(source)

        assert report.compatible
        assert report.source_covered
        assert report.parsed_without_failures
        assert report.semantic_roundtrip
        assert report.canonical_stable
        assert report.output_encodable
        assert report.exact_source_match is False
        assert report.entry_count == 1
        assert report.diagnostics == ()

    def test_canonical_source_reports_exact_match(self):
        """The report distinguishes byte-stable input from allowed layout cleanup."""
        source = "@article{k,\n\ttitle = {Stable}\n}\n"

        report = check_string(source)

        assert report.compatible
        assert report.exact_source_match

    def test_explicit_parse_failure_is_incompatible(self):
        """Retaining unsupported raw input is safe but not a compatibility pass."""
        report = check_string("@article{broken, title={Retained}")

        assert not report.compatible
        assert report.parsed_without_failures is False
        assert report.semantic_roundtrip is None
        assert report.canonical_stable is None
        assert report.output_encodable is None
        assert [finding.code for finding in report.diagnostics] == ["parse-failure"]
        assert report.diagnostics[0].line == 1

    def test_unstable_output_cannot_receive_a_compatible_result(self, monkeypatch):
        """A writer that changes its output on a second cycle is detected."""
        outputs = iter(
            [
                "@article{k,\n\ttitle = {Kept}\n}\n",
                "@article{k,\n}\n",
            ]
        )
        monkeypatch.setattr(compatibility, "write_string", lambda library: next(outputs))

        report = compatibility.check_string("@article{k, title={Kept}}")

        assert not report.compatible
        assert report.semantic_roundtrip is True
        assert report.canonical_stable is False
        assert [finding.code for finding in report.diagnostics] == ["unstable-canonical-output"]

    def test_semantic_loss_cannot_receive_a_compatible_result(self, monkeypatch):
        """A stable writer that consistently drops a field still fails the contract."""
        dropped = "@article{k,\n}\n"
        monkeypatch.setattr(
            compatibility,
            "write_string",
            lambda library: dropped,
        )

        report = compatibility.check_string("@article{k, title={Lost}}")

        assert not report.compatible
        assert report.semantic_roundtrip is False
        assert report.canonical_stable is True
        assert [finding.code for finding in report.diagnostics] == ["semantic-roundtrip-mismatch"]

    def test_unrepresented_source_text_is_incompatible(self, monkeypatch):
        """Raw-span coverage independently guards against unrepresented top-level text."""
        original_parse = compatibility.parse_string

        def parse_without_comment(source):
            return original_parse(source.replace("unrepresented prose", ""))

        monkeypatch.setattr(compatibility, "parse_string", parse_without_comment)

        report = compatibility.check_string("unrepresented prose\n@article{k, title={Kept}}")

        assert not report.compatible
        assert report.source_covered is False
        assert report.diagnostics[0].code == "source-coverage-gap"

    def test_decode_failure_reports_no_source_contents(self):
        """Encoding failures are actionable without exposing bibliography bytes."""
        with tempfile.NamedTemporaryFile(suffix="-private.bib", delete=False) as file:
            file.write(b"\xff\xfe")
            path = file.name

        try:
            report = check_file(path, encoding="utf-8")
            serialized = report.to_dict()

            assert not report.compatible
            assert serialized["diagnostics"][0]["code"] == "decode-error"
            assert "private.bib" not in str(serialized)
            assert "\\xff" not in str(serialized)
        finally:
            os.unlink(path)

    def test_file_identity_compares_bytes_in_the_selected_encoding(self):
        """A canonical non-UTF-8 file can still be byte-identical and compatible."""
        source = "@article{k,\n\ttitle = {Müller}\n}\n"
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(source.encode("latin-1"))
            path = file.name

        try:
            report = check_file(path, encoding="latin-1")

            assert report.compatible
            assert report.output_encodable
            assert report.exact_source_match
        finally:
            os.unlink(path)

    def test_unencodable_canonical_output_is_incompatible(self, monkeypatch):
        """A selected output encoding must be able to represent canonical text."""
        monkeypatch.setattr(
            compatibility,
            "write_string",
            lambda library: "@article{k,\n\ttitle = {€}\n}\n",
        )
        with tempfile.NamedTemporaryFile(mode="w", encoding="ascii", delete=False) as file:
            file.write("@article{k, title={ASCII}}")
            path = file.name

        try:
            report = check_file(path, encoding="ascii")

            assert not report.compatible
            assert report.output_encodable is False
            assert report.exact_source_match is None
            assert "encode-error" in [finding.code for finding in report.diagnostics]
        finally:
            os.unlink(path)
