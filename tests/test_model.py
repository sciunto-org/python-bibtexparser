import pickle
from copy import copy
from copy import deepcopy
from textwrap import dedent

import pytest

import bibtexparser
from bibtexparser.middlewares import NameParts
from bibtexparser.model import DuplicateBlockKeyBlock
from bibtexparser.model import DuplicateFieldKeyBlock
from bibtexparser.model import Entry
from bibtexparser.model import ExplicitComment
from bibtexparser.model import Field
from bibtexparser.model import ImplicitComment
from bibtexparser.model import MiddlewareErrorBlock
from bibtexparser.model import ParsingFailedBlock
from bibtexparser.model import Preamble
from bibtexparser.model import String


def test_entry_equality():
    # Equal to itself
    entry_1 = Entry(
        "article",
        "key",
        [Field("field", "value", 1)],
        1,
        "raw",
    )
    assert entry_1 == entry_1
    # Equal to identical entry
    entry_2 = Entry(
        "article",
        "key",
        [Field("field", "value", 1)],
        1,
        "raw",
    )
    assert entry_1 == entry_2
    # Not equal to entry with different entry-type
    entry_3 = Entry(
        "book",
        "key",
        [Field("field", "value", 1)],
        1,
        "raw",
    )
    assert entry_1 != entry_3
    # Not equal to entry with different fields
    entry_4 = Entry(
        "article",
        "key",
        [Field("field", "value", 1), Field("field2", "value", 2)],
        1,
        "raw",
    )
    assert entry_1 != entry_4


def test_entry_copy():
    entry_1 = Entry(
        "article",
        "key",
        [Field("field", "value", 1)],
        1,
        "raw",
    )
    entry_2 = copy(entry_1)
    assert entry_1 == entry_2
    assert entry_1 is not entry_2
    assert entry_1.fields == entry_2.fields


def test_entry_deepcopy():
    entry_1 = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    entry_2 = deepcopy(entry_1)
    assert entry_1 == entry_2
    assert entry_1 is not entry_2
    assert entry_1.fields is not entry_2.fields
    assert entry_1.fields == entry_2.fields
    assert entry_1.fields_dict["field"] is not entry_2.fields_dict["field"]
    assert entry_1.fields_dict["field"] == entry_2.fields_dict["field"]


def test_entry_get():
    entry1 = Entry("article", "key", [Field("field", "value", 1), Field("foo", "bar", 2)], 1, "raw")
    entry2 = Entry("article", "key", [Field("field", "value", 1), Field("foo", "bar", 2)], 1, "raw")
    assert entry1.get("other", "default") == "default"
    assert entry1.get("foo") == Field("foo", "bar", 2)
    assert entry1 == entry2


def test_entry_pop():
    entry1 = Entry("article", "key", [Field("field", "value", 1), Field("foo", "bar", 2)], 1, "raw")
    entry2 = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    assert entry1.pop("other", "default") == "default"
    assert entry1.pop("foo") == Field("foo", "bar", 2)
    assert entry1 == entry2


def test_entry_contains():
    entry = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    assert "field" in entry
    assert "other" not in entry
    # ENTRYTYPE and ID are exposed by `__getitem__`, hence always contained
    assert "ENTRYTYPE" in entry
    assert "ID" in entry


def test_entry_setitem_field():
    entry = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    entry["field"] = "new_value"
    entry["other"] = "other_value"
    assert entry["field"] == "new_value"
    assert entry["other"] == "other_value"
    assert [f.key for f in entry.fields] == ["field", "other"]


def test_entry_setitem_entrytype_and_id():
    entry = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    entry["ENTRYTYPE"] = "book"
    entry["ID"] = "new_key"
    assert entry.entry_type == "book"
    assert entry.key == "new_key"
    assert entry["ENTRYTYPE"] == "book"
    assert entry["ID"] == "new_key"
    # No literal fields must be created for these keys
    assert [f.key for f in entry.fields] == ["field"]


def test_string_equality():
    # Equal to itself
    string_1 = String(
        "key",
        "value",
        1,
        "raw",
    )
    assert string_1 == string_1
    # Equal to identical string
    string_2 = String(
        "key",
        "value",
        1,
        "raw",
    )
    assert string_1 == string_2
    # Not equal to string with different key
    string_3 = String(
        "key2",
        "value",
        1,
        "raw",
    )
    assert string_1 != string_3
    # Not equal to string with different value
    string_4 = String(
        "key",
        "value2",
        1,
        "raw",
    )
    assert string_1 != string_4


def test_string_copy():
    string_1 = String(
        "key",
        "value",
        1,
        "raw",
    )
    string_2 = copy(string_1)
    assert string_1 == string_2
    assert string_1 is not string_2


def test_string_deepcopy():
    string_1 = String(
        "key",
        "value",
        1,
        "raw",
    )
    string_2 = deepcopy(string_1)
    assert string_1 == string_2
    assert string_1 is not string_2


def test_preamble_equality():
    # Equal to itself
    preamble_1 = Preamble("value", 1, "raw")
    assert preamble_1 == preamble_1
    # Equal to identical preamble
    preamble_2 = Preamble("value", 1, "raw")
    assert preamble_1 == preamble_2
    # Not equal to preamble with different value
    preamble_3 = Preamble("value2", 1, "raw")
    assert preamble_1 != preamble_3


def test_preamble_copy():
    preamble_1 = Preamble("value", 1, "raw")
    preamble_2 = copy(preamble_1)
    assert preamble_1 == preamble_2
    assert preamble_1 is not preamble_2


def test_preable_deepcopy():
    preamble_1 = Preamble("value", 1, "raw")
    preamble_2 = deepcopy(preamble_1)
    assert preamble_1 == preamble_2
    assert preamble_1 is not preamble_2


def test_implicit_comment_equality():
    # Equal to itself
    comment_1 = ImplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    assert comment_1 == comment_1
    # Equal to identical comment
    comment_2 = ImplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    assert comment_1 == comment_2
    # Not equal to comment with different comment
    comment_3 = ImplicitComment(
        start_line=1, comment="This is my comment2", raw="#  This is my comment"
    )
    assert comment_1 != comment_3


def test_implicit_comment_copy():
    comment_1 = ImplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    comment_2 = copy(comment_1)
    assert comment_1 == comment_2
    assert comment_1 is not comment_2


def test_implicit_comment_deepcopy():
    comment_1 = ImplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    comment_2 = deepcopy(comment_1)
    assert comment_1 == comment_2
    assert comment_1 is not comment_2


def test_explicit_comment_equality():
    # Equal to itself
    comment_1 = ExplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    assert comment_1 == comment_1
    # Equal to identical comment
    comment_2 = ExplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    assert comment_1 == comment_2
    # Not equal to comment with different comment
    comment_3 = ExplicitComment(
        start_line=1, comment="This is my comment2", raw="#  This is my comment"
    )
    assert comment_1 != comment_3


def test_explicit_comment_copy():
    comment_1 = ExplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    comment_2 = copy(comment_1)
    assert comment_1 == comment_2
    assert comment_1 is not comment_2


def test_explicit_comment_deepcopy():
    comment_1 = ExplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    comment_2 = deepcopy(comment_1)
    assert comment_1 == comment_2
    assert comment_1 is not comment_2


def test_implicit_and_explicit_comment_equality():
    # Equal to itself
    comment_1 = ImplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    comment_2 = ExplicitComment(
        start_line=1, comment="This is my comment", raw="#  This is my comment"
    )
    assert comment_1 != comment_2
    assert comment_2 != comment_1


def test_string_str():
    string = String("myKey", "myValue", 1, "raw")
    assert str(string) == "String (line: 1, key: `myKey`): `myValue`"


def test_preable_str():
    preamble = Preamble("myValue", 1)
    assert str(preamble) == "Preamble (line: 1): `myValue`"

    preamble = Preamble("myNewPreamble")
    assert str(preamble) == "Preamble (line: None): `myNewPreamble`"


def test_implicit_comment_str():
    comment = ImplicitComment("myComment", 1)
    assert str(comment) == "ImplicitComment (line: 1): `myComment`"


def test_explicit_comment_str():
    comment = ExplicitComment("myComment", 1)
    assert str(comment) == "ExplicitComment (line: 1): `myComment`"


def test_field_str():
    field = Field("myKey", "myValue")
    assert str(field) == "Field (line: None, key: `myKey`): `myValue`"


def test_entry_str():
    entry = Entry(
        entry_type="article",
        key="myEntry",
        fields=[
            Field("myFirstField", "firstValue"),
            Field("mySecondField", "secondValue"),
        ],
    )

    expected = dedent("""\
    Entry (line: None, type: `article`, key: `myEntry`):
    \t`myFirstField` = `firstValue`
    \t`mySecondField` = `secondValue`""")

    assert str(entry) == expected


@pytest.mark.parametrize("enclosing", ["{", '"', "no-enclosing", None])
def test_field_enclosing_demand(enclosing):
    # Default is None (writer middleware decides)
    field = Field("month", "jan")
    assert field.enclosing is None

    # Settable via attribute and constructor
    field.enclosing = enclosing
    assert field.enclosing == enclosing
    assert Field("month", "jan", enclosing=enclosing).enclosing == enclosing

    # Assigning a new value resets the demanded enclosing
    field.value = "feb"
    assert field.enclosing is None


def test_field_enclosing_validation():
    field = Field("month", "jan")
    with pytest.raises(ValueError):
        field.enclosing = "invalid"
    with pytest.raises(ValueError):
        Field("month", "jan", enclosing="invalid")


def test_field_equality_considers_enclosing():
    assert Field("month", "jan") != Field("month", "jan", enclosing="no-enclosing")
    assert Field("month", "jan", enclosing="{") == Field("month", "jan", enclosing="{")


@pytest.mark.parametrize("enclosing", ["{", '"', "no-enclosing", None])
def test_string_enclosing_demand(enclosing):
    # Default is None (writer middleware decides)
    string = String("myKey", "myValue", 1, "raw")
    assert string.enclosing is None

    # Settable via attribute and constructor
    string.enclosing = enclosing
    assert string.enclosing == enclosing
    assert String("myKey", "myValue", 1, "raw", enclosing=enclosing).enclosing == enclosing

    # Assigning a new value resets the demanded enclosing
    string.value = "myNewValue"
    assert string.enclosing is None


def test_string_enclosing_validation():
    string = String("myKey", "myValue", 1, "raw")
    with pytest.raises(ValueError):
        string.enclosing = "invalid"
    with pytest.raises(ValueError):
        String("myKey", "myValue", 1, "raw", enclosing="invalid")


def test_entry_hash():
    # Equal entries have equal hashes
    entry_1 = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    entry_2 = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    assert hash(entry_1) == hash(entry_2)
    # Entries are usable in sets and dicts
    assert len({entry_1, deepcopy(entry_1)}) == 1
    assert {entry_1: "value"}[entry_2] == "value"


def test_string_hash():
    # Equal strings have equal hashes
    string_1 = String("key", "value", 1, "raw")
    string_2 = String("key", "value", 1, "raw")
    assert hash(string_1) == hash(string_2)
    # Strings are usable in sets and dicts
    assert len({string_1, deepcopy(string_1)}) == 1
    assert {string_1: "value"}[string_2] == "value"


def test_field_hash():
    # Equal fields have equal hashes
    field_1 = Field("field", "value", 1)
    field_2 = Field("field", "value", 1)
    assert hash(field_1) == hash(field_2)
    # Fields are usable in sets and dicts, even with unhashable values
    field_1.value = ["some", "unhashable", "value"]
    assert len({field_1, deepcopy(field_1)}) == 1
    assert {field_1: "value"}[deepcopy(field_1)] == "value"


def test_programmatically_created_blocks_have_distinct_hashes():
    """Blocks without start_line/raw must not all collide. See issue 565."""
    entries = [Entry("article", f"key_{i}", [Field("field", "value")]) for i in range(100)]
    assert len({hash(entry) for entry in entries}) == 100
    assert hash(Entry("article", "key", [])) != hash(Entry("book", "key", []))

    strings = [String(f"key_{i}", "value") for i in range(100)]
    assert len({hash(string) for string in strings}) == 100

    preambles = [Preamble(f"value_{i}") for i in range(100)]
    assert len({hash(preamble) for preamble in preambles}) == 100

    explicit_comments = [ExplicitComment(f"comment_{i}") for i in range(100)]
    assert len({hash(comment) for comment in explicit_comments}) == 100

    implicit_comments = [ImplicitComment(f"comment_{i}") for i in range(100)]
    assert len({hash(comment) for comment in implicit_comments}) == 100

    fields = [Field(f"key_{i}", "value") for i in range(100)]
    assert len({hash(field) for field in fields}) == 100


def test_equal_blocks_have_equal_hashes():
    """The hash invariant: `a == b` implies `hash(a) == hash(b)`."""
    equal_pairs = [
        (
            Entry("article", "key", [Field("field", "value")]),
            Entry("article", "key", [Field("field", "value")]),
        ),
        (String("key", "value"), String("key", "value")),
        (Preamble("value"), Preamble("value")),
        (ExplicitComment("comment"), ExplicitComment("comment")),
        (ImplicitComment("comment"), ImplicitComment("comment")),
        (Field("key", "value"), Field("key", "value")),
    ]
    for first, second in equal_pairs:
        assert first == second
        assert hash(first) == hash(second)
        assert hash(first) == hash(deepcopy(first))
        assert hash(first) == hash(copy(first))


def test_parsed_block_hashes_equal_to_identically_constructed_block():
    """A parsed block and an identically constructed one are equal, hence hash equal."""
    library = bibtexparser.parse_string("@article{key,\n  field = {value},\n}\n")
    parsed_entry = library.entries[0]
    constructed_entry = Entry(
        entry_type="article",
        key="key",
        fields=[Field("field", "value", start_line=1)],
        start_line=0,
        raw="@article{key,\n  field = {value},\n}",
    )
    constructed_entry.set_parser_metadata("removed_enclosing", {"field": "{"})
    assert parsed_entry == constructed_entry
    assert hash(parsed_entry) == hash(constructed_entry)


def test_hash_of_blocks_with_unhashable_values():
    """Unhashable field values (e.g. after middleware) must not break hashing."""
    list_valued = Entry("article", "key", [Field("author", ["Doe, John", "Roe, Jane"])])
    assert isinstance(hash(list_valued), int)

    name_parts_valued = Entry(
        "article", "key", [Field("author", [NameParts(first=["John"], last=["Doe"])])]
    )
    assert isinstance(hash(name_parts_valued), int)

    assert isinstance(hash(Field("author", ["Doe, John"])), int)
    assert isinstance(hash(Field("author", NameParts(last=["Doe"]))), int)

    with_metadata = Entry("article", "key", [])
    with_metadata.set_parser_metadata("some_key", ["some", "unhashable", "value"])
    assert isinstance(hash(with_metadata), int)


def test_blocks_in_sets_and_dicts():
    """Distinct blocks are kept apart, equal blocks are deduplicated."""
    first = Entry("article", "first", [Field("field", "value")])
    second = Entry("article", "second", [Field("field", "value")])
    assert len({first, second}) == 2
    assert len({first, second, deepcopy(first)}) == 2

    block_dict = {first: "first_value", second: "second_value"}
    assert block_dict[deepcopy(first)] == "first_value"
    assert block_dict[deepcopy(second)] == "second_value"

    blocks = [
        Entry("article", "same", []),
        String("same", "same"),
        Preamble("same"),
        ExplicitComment("same"),
        ImplicitComment("same"),
    ]
    assert len(set(blocks)) == len(blocks)


def test_entry_fields_shorthand():
    entry = Entry(
        entry_type="article",
        key="myEntry",
        fields=[
            Field("myFirstField", "firstValue"),
            Field("mySecondField", "secondValue"),
        ],
    )

    entry["myFirstField"] = "changed_value"
    assert entry["myFirstField"] == "changed_value"
    assert entry.fields_dict["myFirstField"].value == "changed_value"

    entry["myNewField"] = "new_value"
    assert entry["myNewField"] == "new_value"
    assert entry.fields_dict["myNewField"].key == "myNewField"
    assert entry.fields_dict["myNewField"].value == "new_value"
    assert entry.fields_dict["myNewField"].start_line is None

    del entry["myNewField"]
    assert "myNewField" not in entry.fields_dict
    assert len([f for f in entry.fields if f.key == "myNewField"]) == 0
    with pytest.raises(KeyError):
        entry["myNewField"]


# --- Deep-copying of blocks and fields ---------------------------------------
# Blocks and fields implement a fast `__deepcopy__` (middleware deep-copies every
# block by default). The following tests ensure it behaves like the generic one.


def _all_block_types():
    entry = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    entry.set_parser_metadata("meta", {"nested": ["list"]})
    return [
        entry,
        String("key", "value", 2, "raw", enclosing="{"),
        Preamble("value", 3, "raw"),
        ExplicitComment("comment", 4, "raw"),
        ImplicitComment("comment", 5, "raw"),
        ParsingFailedBlock(ValueError("error"), 6, "raw"),
        MiddlewareErrorBlock(Entry("article", "key", []), ValueError("error")),
        DuplicateBlockKeyBlock("key", Entry("article", "key", []), Entry("book", "key", []), 7),
        DuplicateFieldKeyBlock(
            {"a", "b"}, Entry("article", "key", [Field("a", "1"), Field("a", "2")])
        ),
    ]


def _assert_same_state(block, other):
    """Asserts that two distinct block instances carry the same state.

    Blocks holding an exception (``ParsingFailedBlock``) are never ``==``
    to a copy of themselves, as exceptions compare by identity only."""
    assert block is not other
    assert type(block) is type(other)
    if isinstance(block, ParsingFailedBlock):
        assert type(block.error) is type(other.error)
        assert str(block.error) == str(other.error)
        assert block.error is not other.error
        state = {key: value for key, value in block.__dict__.items() if key != "_error"}
        other_state = {key: value for key, value in other.__dict__.items() if key != "_error"}
        assert state == other_state
    else:
        assert block == other


@pytest.mark.parametrize("block", _all_block_types(), ids=lambda b: type(b).__name__)
def test_block_deepcopy_is_equal_but_independent(block):
    block_copy = deepcopy(block)

    _assert_same_state(block_copy, block)
    assert hash(block_copy) == hash(block)
    assert block_copy.__dict__.keys() == block.__dict__.keys()
    # Mutable attributes are copied, not shared
    assert block_copy.parser_metadata is not block.parser_metadata
    block_copy.set_parser_metadata("added", True)
    assert block.get_parser_metadata("added") is None
    assert block_copy != block


@pytest.mark.parametrize("block", _all_block_types(), ids=lambda b: type(b).__name__)
def test_block_deepcopy_matches_pickle_roundtrip(block):
    # Pickling reconstructs all state the way the generic `copy.deepcopy` does.
    pickled_copy = pickle.loads(pickle.dumps(block))
    deep_copy = deepcopy(block)
    _assert_same_state(deep_copy, pickled_copy)


def test_entry_deepcopy_nested_values_are_independent():
    entry = Entry("article", "key", [Field("field", "value", 1)], 1, "raw")
    entry.set_parser_metadata("meta", {"nested": ["list"]})
    entry_copy = deepcopy(entry)

    entry_copy.fields.append(Field("new", "value"))
    entry_copy.fields[0].value = "changed"
    entry_copy.parser_metadata["meta"]["nested"].append("added")
    assert len(entry.fields) == 1
    assert entry.fields[0].value == "value"
    assert entry.parser_metadata == {"meta": {"nested": ["list"]}}

    entry.fields[0].key = "renamed"
    entry.set_parser_metadata("other", 1)
    assert entry_copy.fields[0].key == "field"
    assert entry_copy.get_parser_metadata("other") is None


@pytest.mark.parametrize(
    "value",
    [
        ["Doe, John", "Smith, Jane"],
        [NameParts(first=["John"], last=["Doe"]), NameParts(first=["Jane"], last=["Smith"])],
        NameParts(first=["John"], von=["von"], last=["Doe"], jr=["Jr."]),
        ("a", "tuple"),
        {"a": ["dict"]},
    ],
    ids=["list", "nameparts_list", "nameparts", "tuple", "dict"],
)
def test_field_deepcopy_non_primitive_values_are_deep_copied(value):
    field = Field("author", value, 1, enclosing="{")
    field_copy = deepcopy(field)

    assert field_copy == field
    assert field_copy is not field
    assert field_copy.value == value
    assert field_copy.key == "author"
    assert field_copy.start_line == 1
    assert field_copy.enclosing == "{"
    if isinstance(value, tuple):
        # Tuples of immutables are shared by the generic `copy.deepcopy` as well
        return
    assert field_copy.value is not field.value
    if isinstance(value, list):
        original_length = len(value)
        field_copy.value.append("added")
        assert len(field.value) == original_length
        if isinstance(value[0], NameParts):
            assert field_copy.value[0] is not field.value[0]
            field_copy.value[0].first.append("added")
            assert field.value[0].first == ["John"]
    if isinstance(value, NameParts):
        field_copy.value.first.append("added")
        assert field.value.first == ["John"]
    if isinstance(value, dict):
        field_copy.value["a"].append("added")
        assert field.value == {"a": ["dict"]}


def test_field_deepcopy_shares_immutable_primitives():
    # Same behavior as generic `copy.deepcopy`: atomic values are not duplicated
    field = Field("key", "value", 1, enclosing="{")
    field_copy = deepcopy(field)
    assert field_copy.value is field.value
    assert field_copy.key is field.key
    assert field_copy.enclosing is field.enclosing
    # Changing the copy does not affect the original
    field_copy.value = "new value"
    assert field.value == "value"
    assert field.enclosing == "{"
    assert field_copy.enclosing is None


def test_deepcopy_memo_keeps_shared_references_shared():
    previous = Entry("article", "key", [Field("field", "value")], 1, "raw")
    duplicate = Entry("article", "key", [Field("field", "other")], 2, "raw2")
    error_block = DuplicateBlockKeyBlock("key", previous, duplicate, 2, "raw2")

    previous_copy, error_block_copy = deepcopy([previous, error_block])

    assert error_block_copy.previous_block is previous_copy
    assert error_block_copy.previous_block is not previous
    assert error_block_copy.ignore_error_block == duplicate
    assert error_block_copy.ignore_error_block is not duplicate
    assert error_block_copy.error is not error_block.error
    assert str(error_block_copy.error) == str(error_block.error)

    # A block deep-copied on its own also deep-copies the referenced blocks
    lone_copy = deepcopy(error_block)
    assert lone_copy.previous_block == previous
    assert lone_copy.previous_block is not previous


def test_deepcopy_handles_cyclic_references():
    entry = Entry("article", "key", [Field("field", "value")])
    entry.set_parser_metadata("self", entry)
    entry.set_parser_metadata("field", entry.fields[0])

    entry_copy = deepcopy(entry)
    assert entry_copy.get_parser_metadata("self") is entry_copy
    assert entry_copy.get_parser_metadata("field") is entry_copy.fields[0]


def test_deepcopy_of_entry_subclass_yields_subclass():
    class CustomEntry(Entry):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.custom_attribute = ["custom"]

    entry = CustomEntry("article", "key", [Field("field", "value")], 1, "raw")
    entry_copy = deepcopy(entry)

    assert type(entry_copy) is CustomEntry
    assert entry_copy == entry
    assert entry_copy.custom_attribute == ["custom"]
    assert entry_copy.custom_attribute is not entry.custom_attribute
    assert entry_copy.fields == entry.fields
    assert entry_copy.fields is not entry.fields


def test_deepcopy_of_str_subclass_values_is_not_shared():
    class CustomStr(str):
        pass

    field = Field("key", CustomStr("value"))
    field_copy = deepcopy(field)
    assert type(field_copy.value) is CustomStr
    assert field_copy.value == "value"
    assert field_copy.value is not field.value


def test_deepcopy_honours_custom_deepcopy_of_nested_subclass():
    class CustomEntry(Entry):
        def __deepcopy__(self, memo):
            copied = Entry.__deepcopy__(self, memo)
            copied.set_parser_metadata("custom_deepcopy", True)
            return copied

    entry = CustomEntry("article", "key", [Field("field", "value")])
    error_block = DuplicateBlockKeyBlock("key", entry, Entry("article", "key", []))

    error_block_copy = deepcopy(error_block)
    assert type(error_block_copy.previous_block) is CustomEntry
    assert error_block_copy.previous_block.get_parser_metadata("custom_deepcopy") is True
    assert entry.get_parser_metadata("custom_deepcopy") is None
