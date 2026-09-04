"""Testing the parse_file and write_file functions."""

import logging
import os
import tempfile
import warnings

import pytest

from bibtexparser import entrypoint
from bibtexparser import parse_file
from bibtexparser import parse_string
from bibtexparser import write_file
from bibtexparser import write_string
from bibtexparser.entrypoint import LARGE_LIBRARY_WARNING_THRESHOLD
from bibtexparser.library import Library
from bibtexparser.middlewares import MonthAbbreviationMiddleware
from bibtexparser.middlewares import RemoveEnclosingMiddleware
from bibtexparser.middlewares import SeparateCoAuthors
from bibtexparser.middlewares import default_unparse_stack
from bibtexparser.model import DuplicateBlockKeyBlock
from bibtexparser.model import Entry
from bibtexparser.model import Field
from bibtexparser.model import String


def test_gbk():
    library = parse_file("tests/resources/gbk_test.bib", encoding="gbk")
    assert library.entries[0]["author"] == "凯撒"
    assert library.entries[0]["title"] == "Test Title"
    assert library.entries[0]["year"] == "2013"
    assert library.entries[0]["journal"] == "测试期刊"


def test_write_file_default_encoding():
    """Test write_file uses UTF-8 by default."""
    entry = Entry(
        entry_type="article",
        key="test2024",
        fields=[
            Field(key="author", value="Müller"),
            Field(key="title", value="Ångström measurements"),
        ],
    )
    library = Library([entry])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        write_file(temp_path, library)
        # Read back and verify
        with open(temp_path, encoding="UTF-8") as f:
            content = f.read()
        assert "Müller" in content
        assert "Ångström" in content
    finally:
        os.unlink(temp_path)


def test_write_file_gbk_encoding():
    """Test write_file with GBK encoding for Chinese characters."""
    entry = Entry(
        entry_type="article",
        key="test2024",
        fields=[
            Field(key="author", value="凯撒"),
            Field(key="title", value="Test Title"),
            Field(key="journal", value="测试期刊"),
        ],
    )
    library = Library([entry])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        write_file(temp_path, library, encoding="gbk")
        # Read back with GBK and verify
        with open(temp_path, encoding="gbk") as f:
            content = f.read()
        assert "凯撒" in content
        assert "测试期刊" in content
    finally:
        os.unlink(temp_path)


def test_write_file_roundtrip_gbk():
    """Test round-trip: parse GBK file, write with GBK, parse again."""
    # Parse original GBK file
    library = parse_file("tests/resources/gbk_test.bib", encoding="gbk")
    original_author = library.entries[0]["author"]
    original_journal = library.entries[0]["journal"]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        # Write with GBK encoding
        write_file(temp_path, library, encoding="gbk")
        # Parse back
        library2 = parse_file(temp_path, encoding="gbk")
        assert library2.entries[0]["author"] == original_author
        assert library2.entries[0]["journal"] == original_journal
    finally:
        os.unlink(temp_path)


# Deprecation warning tests for write_file and write_string
def test_write_file_deprecated_parse_stack_parameter():
    """Test that using deprecated 'parse_stack' parameter issues a warning."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            write_file(temp_path, library, parse_stack=[])
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "parse_stack" in str(w[0].message)
            assert "unparse_stack" in str(w[0].message)
    finally:
        os.unlink(temp_path)


def test_write_file_deprecated_append_middleware_parameter():
    """Test that using deprecated 'append_middleware' parameter issues a warning."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            write_file(temp_path, library, append_middleware=[])
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "append_middleware" in str(w[0].message)
            assert "prepend_middleware" in str(w[0].message)
    finally:
        os.unlink(temp_path)


def test_write_file_both_parse_stack_and_unparse_stack_raises_error():
    """Test that providing both parse_stack and unparse_stack raises ValueError."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as excinfo:
            write_file(temp_path, library, parse_stack=[], unparse_stack=[])
        assert "parse_stack" in str(excinfo.value)
        assert "unparse_stack" in str(excinfo.value)
        assert "Use 'unparse_stack' instead" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_write_file_both_append_and_prepend_middleware_raises_error():
    """Test that providing both append_middleware and prepend_middleware raises ValueError."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as excinfo:
            write_file(temp_path, library, append_middleware=[], prepend_middleware=[])
        assert "append_middleware" in str(excinfo.value)
        assert "prepend_middleware" in str(excinfo.value)
        assert "Use 'prepend_middleware' instead" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_write_file_unexpected_keyword_argument_raises_error():
    """Test that unexpected keyword arguments raise TypeError."""
    library = Library([])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(TypeError) as excinfo:
            write_file(temp_path, library, unknown_param="value")
        assert "unexpected keyword arguments" in str(excinfo.value)
        assert "unknown_param" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


def test_write_string_deprecated_parse_stack_parameter():
    """Test that using deprecated 'parse_stack' parameter issues a warning."""
    library = Library([])

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        write_string(library, parse_stack=[])
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "parse_stack" in str(w[0].message)
        assert "unparse_stack" in str(w[0].message)


def test_write_string_deprecated_append_middleware_parameter():
    """Test that using deprecated 'append_middleware' parameter issues a warning."""
    library = Library([])

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        write_string(library, append_middleware=[])
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "append_middleware" in str(w[0].message)
        assert "prepend_middleware" in str(w[0].message)


def test_write_string_both_parse_stack_and_unparse_stack_raises_error():
    """Test that providing both parse_stack and unparse_stack raises ValueError."""
    library = Library([])

    with pytest.raises(ValueError) as excinfo:
        write_string(library, parse_stack=[], unparse_stack=[])
    assert "parse_stack" in str(excinfo.value)
    assert "unparse_stack" in str(excinfo.value)
    assert "Use 'unparse_stack' instead" in str(excinfo.value)


def test_write_string_both_append_and_prepend_middleware_raises_error():
    """Test that providing both append_middleware and prepend_middleware raises ValueError."""
    library = Library([])

    with pytest.raises(ValueError) as excinfo:
        write_string(library, append_middleware=[], prepend_middleware=[])
    assert "append_middleware" in str(excinfo.value)
    assert "prepend_middleware" in str(excinfo.value)
    assert "Use 'prepend_middleware' instead" in str(excinfo.value)


def test_write_string_unexpected_keyword_argument_raises_error():
    """Test that unexpected keyword arguments raise TypeError."""
    library = Library([])

    with pytest.raises(TypeError) as excinfo:
        write_string(library, unknown_param="value")
    assert "unexpected keyword arguments" in str(excinfo.value)
    assert "unknown_param" in str(excinfo.value)


FIRST_BIBTEX = """@string{me = "My Name"}

@article{first,
    title = {Hello World},
    author = me,
    year = 2023
}"""


def test_parse_string_into_existing_library_returns_the_passed_library():
    """The passed library is mutated and returned, no new instance is created."""
    library = parse_string(FIRST_BIBTEX)
    returned = parse_string("@article{second, title = {Second}}", library=library)
    assert returned is library


def test_parse_string_into_existing_library_keeps_previous_blocks_untouched():
    """Blocks already in the library must not be transformed a second time."""
    library = parse_string(FIRST_BIBTEX)
    first_entry = library.entries_dict["first"]
    first_string = library.strings_dict["me"]

    parse_string("@article{second, title = {Second}}", library=library)

    assert library.entries_dict["first"] is first_entry
    assert library.strings_dict["me"] is first_string
    assert first_entry["title"] == "Hello World"
    assert first_entry["author"] == "My Name"
    assert first_entry["year"] == "2023"
    assert first_string.value == "My Name"
    assert all(field.enclosing is None for field in first_entry.fields)
    assert first_string.enclosing is None


def test_parse_string_into_existing_library_does_not_warn():
    """The parse stack must not be re-applied, hence no enclosing-order warning."""
    library = parse_string(FIRST_BIBTEX)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        parse_string("@article{second, title = {Second}, author = me}", library=library)
    assert [str(warning.message) for warning in w] == []


def test_parse_string_into_existing_library_roundtrips():
    """The resulting library must still serialize to valid (re-parsable) bibtex."""
    library = parse_string(FIRST_BIBTEX)
    parse_string("@article{second, title = {Second}, author = me}", library=library)

    written = write_string(library)
    assert "title = {Hello World}" in written
    assert "author = {My Name}" in written
    assert "@string{me = {My Name}}" in written

    reparsed = parse_string(written)
    assert reparsed.failed_blocks == []
    assert reparsed.entries_dict["first"]["title"] == "Hello World"
    assert reparsed.entries_dict["first"]["author"] == "My Name"
    assert reparsed.entries_dict["second"]["author"] == "My Name"
    assert reparsed.strings_dict["me"].value == "My Name"


def test_parse_string_into_existing_library_is_equivalent_to_parsing_at_once():
    """Parsing in two steps must yield the same bibtex as parsing everything at once."""
    second_bibtex = "@article{second, title = {Second}, author = me}"

    stepwise = parse_string(FIRST_BIBTEX)
    parse_string(second_bibtex, library=stepwise)
    at_once = parse_string(FIRST_BIBTEX + "\n\n" + second_bibtex)

    assert write_string(stepwise) == write_string(at_once)


def test_parse_string_into_existing_library_resolves_previously_defined_strings():
    """String references in the new content resolve against earlier @string blocks."""
    library = parse_string(FIRST_BIBTEX)
    parse_string("@article{second, author = me}", library=library)

    assert library.entries_dict["second"]["author"] == "My Name"
    assert len(library.strings) == 1
    assert [type(block) for block in library.blocks].count(String) == 1


def test_parse_string_into_existing_library_resolves_strings_case_insensitively():
    """As within a single parse, string references are case-insensitive."""
    library = parse_string(FIRST_BIBTEX)
    parse_string("@article{second, author = ME}", library=library)
    assert library.entries_dict["second"]["author"] == "My Name"


def test_parse_string_repeatedly_into_existing_library():
    """More than two consecutive calls keep working (no accumulating corruption)."""
    library = parse_string(FIRST_BIBTEX)
    for key in ("second", "third", "fourth"):
        parse_string(f"@article{{{key}, author = me}}", library=library)

    assert len(library.entries) == 4
    assert library.failed_blocks == []
    assert all(entry["author"] == "My Name" for entry in library.entries)
    assert write_string(library).count("author = {My Name}") == 4


def test_parse_string_into_existing_library_duplicate_entry_key():
    """A duplicate entry key across two calls yields a DuplicateBlockKeyBlock."""
    library = parse_string("@article{duplicate, title = {First}}")
    parse_string("@article{duplicate, title = {Second}}", library=library)

    assert len(library.failed_blocks) == 1
    failed = library.failed_blocks[0]
    assert isinstance(failed, DuplicateBlockKeyBlock)
    assert failed.key == "duplicate"
    assert library.entries_dict["duplicate"]["title"] == "First"


def test_parse_string_into_existing_library_redefined_string_key():
    """A @string redefined by the new content becomes a DuplicateBlockKeyBlock,
    but is used to resolve references within the newly parsed content."""
    library = parse_string('@string{me = "Old"}\n@article{first, author = me}')
    parse_string('@string{me = "New"}\n@article{second, author = me}', library=library)

    assert library.strings_dict["me"].value == "Old"
    assert len(library.failed_blocks) == 1
    assert isinstance(library.failed_blocks[0], DuplicateBlockKeyBlock)
    assert library.failed_blocks[0].key == "me"

    assert library.entries_dict["first"]["author"] == "Old"
    assert library.entries_dict["second"]["author"] == "New"


def test_parse_string_into_manually_created_library():
    """Strings of a hand-built (never parsed) library are usable as references."""
    library = Library(
        [
            Entry("article", "manual", [Field("title", "Manual")]),
            String("manual_string", "Some Value"),
        ]
    )
    parse_string("@article{parsed, author = manual_string}", library=library)

    assert library.entries_dict["parsed"]["author"] == "Some Value"
    assert library.entries_dict["manual"]["title"] == "Manual"
    assert "author = {Some Value}" in write_string(library)


def test_parse_string_into_existing_library_keeps_block_order():
    """Newly parsed blocks are appended after the pre-existing ones."""
    library = parse_string("% first comment\n@article{first, title = {First}}")
    parse_string("% second comment\n@article{second, title = {Second}}", library=library)

    assert [block.__class__.__name__ for block in library.blocks] == [
        "ImplicitComment",
        "Entry",
        "ImplicitComment",
        "Entry",
    ]
    assert [entry.key for entry in library.entries] == ["first", "second"]


def _library_with_n_entries(n: int) -> Library:
    return Library(
        [
            Entry(entry_type="article", key=f"key{i}", fields=[Field(key="title", value="T")])
            for i in range(n)
        ]
    )


def test_large_library_warning_threshold_is_reasonable():
    assert 1_000 <= LARGE_LIBRARY_WARNING_THRESHOLD <= 100_000


def test_write_string_warns_for_large_library_with_copying_stack(monkeypatch, caplog):
    """The default unparse stack deep-copies blocks, which is slow for large libraries."""
    monkeypatch.setattr("bibtexparser.entrypoint.LARGE_LIBRARY_WARNING_THRESHOLD", 5)
    library = _library_with_n_entries(5)

    with caplog.at_level(logging.WARNING, logger="bibtexparser.entrypoint"):
        write_string(library)

    warnings_ = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings_) == 1
    assert "Writing a library with 5 blocks" in warnings_[0].message
    assert "allow_inplace_modification=True" in warnings_[0].message


def test_write_file_warns_for_large_library_with_copying_stack(monkeypatch, caplog):
    monkeypatch.setattr("bibtexparser.entrypoint.LARGE_LIBRARY_WARNING_THRESHOLD", 5)
    library = _library_with_n_entries(5)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        temp_path = f.name
    try:
        with caplog.at_level(logging.WARNING, logger="bibtexparser.entrypoint"):
            write_file(temp_path, library)
    finally:
        os.unlink(temp_path)

    assert caplog.text.count("Writing a library with 5 blocks") == 1


def test_write_string_does_not_warn_below_threshold(monkeypatch, caplog):
    monkeypatch.setattr("bibtexparser.entrypoint.LARGE_LIBRARY_WARNING_THRESHOLD", 5)
    library = _library_with_n_entries(4)

    with caplog.at_level(logging.WARNING, logger="bibtexparser.entrypoint"):
        write_string(library)

    assert "Writing a library" not in caplog.text


def test_write_string_does_not_warn_with_inplace_stack(monkeypatch, caplog):
    """The suggested workaround must itself not warn, and must produce identical output."""
    expected = write_string(_library_with_n_entries(5))
    monkeypatch.setattr("bibtexparser.entrypoint.LARGE_LIBRARY_WARNING_THRESHOLD", 5)

    with caplog.at_level(logging.WARNING, logger="bibtexparser.entrypoint"):
        actual = write_string(
            _library_with_n_entries(5),
            unparse_stack=default_unparse_stack(allow_inplace_modification=True),
        )

    assert "Writing a library" not in caplog.text
    assert actual == expected


MONTH_BIBTEX = "@article{a, month = {January}, title = {T}}"


def test_write_string_with_inplace_prepend_middleware_does_not_mutate_library():
    """An in-place middleware prepended to the (copying) default stack must not
    leak its modifications into the caller's library."""
    library = parse_string(MONTH_BIBTEX)

    bib_str = write_string(library, prepend_middleware=[MonthAbbreviationMiddleware()])

    assert "month = jan" in bib_str
    assert library.entries[0]["month"] == "January"


def test_write_file_with_inplace_prepend_middleware_does_not_mutate_library(tmp_path):
    library = parse_string(MONTH_BIBTEX)
    path = tmp_path / "out.bib"

    write_file(str(path), library, prepend_middleware=[MonthAbbreviationMiddleware()])

    assert "month = jan" in path.read_text(encoding="UTF-8")
    assert library.entries[0]["month"] == "January"


def test_write_string_default_stack_does_not_mutate_library():
    library = parse_string(MONTH_BIBTEX)

    write_string(library)

    # An in-place AddEnclosingMiddleware would have turned this into "{January}".
    assert library.entries[0]["month"] == "January"
    assert library.entries[0]["title"] == "T"


def test_write_string_all_inplace_stack_may_mutate_library():
    """A stack in which every middleware allows in-place modification is the
    caller's explicit opt-in to skip copying."""
    library = parse_string(MONTH_BIBTEX)
    stack = [MonthAbbreviationMiddleware()] + default_unparse_stack(allow_inplace_modification=True)

    write_string(library, unparse_stack=stack)

    assert library.entries[0]["month"] == "jan"


def test_write_string_copying_stack_gets_no_upfront_copy(monkeypatch):
    """No extra upfront copy if every middleware already copies on its own."""
    library = parse_string(MONTH_BIBTEX)
    monkeypatch.setattr(
        entrypoint, "deepcopy", lambda *args, **kwargs: pytest.fail("unexpected upfront copy")
    )

    write_string(library, unparse_stack=default_unparse_stack(allow_inplace_modification=False))
    write_string(library)


COAUTHOR_BIBTEX = "@article{a, author = {Amy and Bob}, month = {January}, title = {T}}"


def test_parse_string_accepts_generator_append_middleware():
    """A one-shot iterator must not be silently exhausted before it is applied."""
    library = parse_string(COAUTHOR_BIBTEX, append_middleware=iter([SeparateCoAuthors()]))
    assert library.entries[0]["author"] == ["Amy", "Bob"]


def test_parse_string_accepts_generator_parse_stack():
    stack = [RemoveEnclosingMiddleware(), SeparateCoAuthors()]
    library = parse_string(COAUTHOR_BIBTEX, parse_stack=(m for m in stack))
    assert library.entries[0]["author"] == ["Amy", "Bob"]


def test_parse_file_accepts_generator_append_middleware(tmp_path):
    path = tmp_path / "in.bib"
    path.write_text(COAUTHOR_BIBTEX, encoding="UTF-8")

    library = parse_file(str(path), append_middleware=(m for m in [SeparateCoAuthors()]))
    assert library.entries[0]["author"] == ["Amy", "Bob"]


def test_write_string_accepts_generator_prepend_middleware():
    library = parse_string(MONTH_BIBTEX)

    bib_str = write_string(library, prepend_middleware=iter([MonthAbbreviationMiddleware()]))

    assert "month = jan" in bib_str


def test_write_string_accepts_generator_unparse_stack():
    library = parse_string(MONTH_BIBTEX)

    bib_str = write_string(
        library, unparse_stack=(m for m in default_unparse_stack(allow_inplace_modification=False))
    )

    assert "month = {January}" in bib_str


def test_write_file_accepts_generator_prepend_middleware(tmp_path):
    library = parse_string(MONTH_BIBTEX)
    path = tmp_path / "out.bib"

    write_file(str(path), library, prepend_middleware=(m for m in [MonthAbbreviationMiddleware()]))

    assert "month = jan" in path.read_text(encoding="UTF-8")


def test_parse_string_with_generators_for_both_stack_and_append_raises_error():
    with pytest.raises(ValueError) as excinfo:
        parse_string(
            COAUTHOR_BIBTEX,
            parse_stack=iter([]),
            append_middleware=iter([SeparateCoAuthors()]),
        )
    assert "append_middleware" in str(excinfo.value)


def test_write_string_with_generators_for_both_stack_and_prepend_raises_error():
    with pytest.raises(ValueError) as excinfo:
        write_string(
            Library([]),
            unparse_stack=iter([]),
            prepend_middleware=iter([MonthAbbreviationMiddleware()]),
        )
    assert "prepend_middleware" in str(excinfo.value)


def test_parse_string_generator_append_middleware_warns_on_duplicate_type():
    """The duplicate-type warning must still trigger for a one-shot iterator."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        library = parse_string(
            COAUTHOR_BIBTEX, append_middleware=iter([RemoveEnclosingMiddleware()])
        )

    assert any("already in the default parse_stack" in str(warning.message) for warning in w)
    assert library.entries[0]["title"] == "T"
