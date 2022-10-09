from typing import Union

import pytest

from bibtexparser.library import Library
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware, AddEnclosingMiddleware
from bibtexparser.model import String, Entry, Field
from tests.resources import ENCLOSINGS, EDGE_CASE_VALUES


def _skip_pseudo_enclosing_value(value: str):
    starts_and_ends_in_brackets = value.startswith("{") and value.endswith("}")
    starts_and_ends_in_quotes = value.startswith('"') and value.endswith('"')
    if starts_and_ends_in_quotes or starts_and_ends_in_brackets:
        pytest.skip("No enclosing to remove")


@pytest.mark.parametrize("enclosing", ENCLOSINGS +
                         [pytest.param("{0}", id="no_enclosing")])
@pytest.mark.parametrize("value", EDGE_CASE_VALUES)
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_removal_of_enclosing_on_string(enclosing, value, inplace):
    if enclosing == "{0}":
        _skip_pseudo_enclosing_value(value)

    # Create test string
    key = "someKey"
    raw = f"<--- does not matter for this unit test -->"
    start_line = 5

    original = String(start_line=start_line,
                      key=key,
                      raw=raw,
                      value=enclosing.format(value))

    middleware = RemoveEnclosingMiddleware(allow_inplace_modification=inplace)

    transformed_library = middleware.transform(library=Library([original]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.strings) == 1
    # Assert correct removal of enclosing
    transformed = transformed_library.strings[0]
    assert transformed.value == value
    expected_enclosing = enclosing.format("")[0] if enclosing != "{0}" else "no-enclosing"
    assert transformed.parser_metadata["removed_enclosing"] == expected_enclosing
    # Assert remaining fields are unchanged
    assert transformed.start_line == start_line
    assert transformed.key == key
    assert transformed.raw == raw

    # Assert inplace modification
    if inplace:
        # Note that this is not a strict requirement,
        #   as "allow_inplace" does not mandate inplace modification,
        #   but it should be implemented as such for this middleware
        #   for performance reasons.
        assert transformed is original
    else:
        assert transformed is not original


@pytest.mark.parametrize("metadata_enclosing", ["{", '"', "no-enclosing", None])
@pytest.mark.parametrize("default_enclosing", ["{", '"', "no-enclosing"])
@pytest.mark.parametrize("enclose_ints", [True, False], ids=["enclose_ints", "no_enclose_ints"])
@pytest.mark.parametrize("reuse_previous_enclosing", [True, False], ids=["reuse", "no_reuse"])
@pytest.mark.parametrize("value", EDGE_CASE_VALUES + ["1990"])
@pytest.mark.parametrize("inplace", [True, False], ids=["inplace", "not_inplace"])
def test_addition_of_enclosing_on_entry(metadata_enclosing: str,
                                        default_enclosing: str,
                                        enclose_ints: bool,
                                        reuse_previous_enclosing: bool,
                                        value: Union[str, int],
                                        inplace: bool):
    # These values not matter for this unit test, 
    #   but must not change during transformation
    #   (hence, they are created as variables, not directly in Entry constructor)
    entry_type = "article"
    key = "someKey"
    raw = "<--- does not matter for this unit test -->"
    entry_line, field_line = 5, 6

    original = Entry(start_line=entry_line,
                     entry_type="article",
                     raw=raw,
                     key=key,
                     fields={"year": Field(value=value,
                                           start_line=field_line,
                                           key="year")})

    if metadata_enclosing is not None:
        original.parser_metadata["removed_enclosing"] = {
            "year": metadata_enclosing
        }

    middleware = AddEnclosingMiddleware(allow_inplace_modification=inplace,
                                        default_enclosing=default_enclosing,
                                        reuse_previous_enclosing=reuse_previous_enclosing,
                                        enclose_integers=enclose_ints)

    transformed_library = middleware.transform(library=Library([original]))

    # Assert correct library state
    assert len(transformed_library.blocks) == 1
    assert len(transformed_library.entries) == 1
    # Assert correct addition of enclosing
    transformed = transformed_library.entries[0]
    changed_value = transformed.fields["year"].value

    # Figure out which enclosing was added
    if changed_value.startswith('"') and changed_value.endswith('"'):
        used_enclosing = '"'
    elif changed_value.startswith('{') and changed_value.endswith('}'):
        used_enclosing = '{'
    elif str(changed_value) == str(value):
        used_enclosing = "no-enclosing"
    else:
        raise ValueError(f"Strange encoding: {changed_value}")

    # Assert correct enclosing was added
    if reuse_previous_enclosing and metadata_enclosing is not None:
        expected_enclosing = metadata_enclosing
    elif (isinstance(value, int) or value.isdigit()) and not enclose_ints:
        expected_enclosing = "no-enclosing"
    else:
        expected_enclosing = default_enclosing

    if expected_enclosing == "no-enclosing":
        _skip_pseudo_enclosing_value(value)

    assert used_enclosing == expected_enclosing
