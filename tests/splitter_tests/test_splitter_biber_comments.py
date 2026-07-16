"""Regression tests for Biber-style percent comments within entries.

Biber permits a line whose first non-whitespace character is ``%`` inside an
entry. Such a line is commentary, even when it resembles a field or contains an
equals sign. Treating it as a regular field can silently absorb the following
field and corrupt both the parsed model and subsequent output.
"""

from pathlib import Path

from bibtexparser import parse_string
from bibtexparser import write_string

RESOURCE = Path(__file__).parents[1] / "resources" / "biber_comments.bib"


class TestBiberEntryComments:
    """Protect comment visibility without exposing comments as bibliography fields."""

    def test_comment_with_equals_sign_does_not_absorb_following_field(self):
        """Comment punctuation cannot change the boundaries of real fields."""
        source = """@article{record,
            author = {Fartsy},
            % explanatory = sign, braces={ignored}
            date = {2024},
        }"""

        entry = parse_string(source).entries_dict["record"]

        assert [(field.key, field.value) for field in entry.fields] == [
            ("author", "Fartsy"),
            ("date", "2024"),
        ]
        assert [comment.comment for comment in entry.comments] == [
            " explanatory = sign, braces={ignored}"
        ]

    def test_commented_out_field_is_not_available_as_data(self):
        """A field-shaped comment remains commentary rather than active data."""
        source = """@online{record,
            %title={Withdrawn title},
            title={Current title},
            url={https://example.invalid},
        }"""

        entry = parse_string(source).entries_dict["record"]

        assert entry["title"] == "Current title"
        assert "%title" not in entry
        assert [comment.comment for comment in entry.comments] == ["title={Withdrawn title},"]

    def test_roundtrip_preserves_comments_at_their_field_boundaries(self):
        """Canonical formatting retains comments before, between, and after fields."""
        source = RESOURCE.read_text(encoding="utf-8")

        written = write_string(parse_string(source))
        reparsed = parse_string(written).entries_dict["record"]

        assert written.index("% before all fields") < written.index("title =")
        assert written.index("title =") < written.index("% between fields")
        assert written.index("% between fields") < written.index("url =")
        assert written.index("url =") < written.index("% after all fields")
        assert [comment.comment for comment in reparsed.comments] == [
            " before all fields",
            " between fields",
            " after all fields",
        ]
        assert [(field.key, field.value) for field in reparsed.fields] == [
            ("title", "Current title"),
            ("date", "2024"),
            ("url", "https://example.invalid"),
        ]

    def test_crlf_comment_does_not_retain_carriage_return(self):
        """The line ending is syntax and must not become part of comment content."""
        source = "@article{record,\r\n  % note\r\n  title={Current title}\r\n}"

        entry = parse_string(source).entries_dict["record"]

        assert [comment.comment for comment in entry.comments] == [" note"]
        assert "\r" not in write_string(parse_string(source))

    def test_top_level_percent_comment_remains_an_implicit_comment(self):
        """The in-entry marker must not consume established top-level comments."""
        source = "% top-level note\n@article{record, title={Current title}}"

        library = parse_string(source)

        assert [comment.comment for comment in library.comments] == ["% top-level note"]
        assert [entry.key for entry in library.entries] == ["record"]

    def test_comment_survives_when_preceding_fields_are_removed(self):
        """Editing fields must move an out-of-range comment boundary, not drop it."""
        library = parse_string(RESOURCE.read_text(encoding="utf-8"))
        entry = library.entries_dict["record"]
        entry.fields = []

        written = write_string(library)

        assert "% before all fields" in written
        assert "% between fields" in written
        assert "% after all fields" in written
