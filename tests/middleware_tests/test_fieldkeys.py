import re

from bibtexparser import Library
from bibtexparser.middlewares.fieldkeys import NormalizeFieldKeys
from bibtexparser.model import Entry
from bibtexparser.model import Field

entries = {
    "article": {
        "author": '"Smith, J."',
        "title": '"A Test Article"',
        "journal": '"J. of Testing"',
        "month": '"jan"',
        "year": '"2022"',
    },
    "book": {
        "author": '"Doe, J."',
        "title": '"A Test Book"',
        "publisher": '"Test Pub."',
        "year": '"2021"',
        "month": "apr",
    },
    "inproceedings": {
        "author": '"Jones, R."',
        "title": '"A Test Conf. Paper"',
        "booktitle": '"Proc. of the Intl. Test Conf."',
        "year": '"2023"',
        "month": "8",
    },
}

ref = Library()
for i, (entry_type, fields) in enumerate(entries.items()):
    f = [Field(key=k, value=v) for k, v in fields.items()]
    ref.add(Entry(entry_type=entry_type, key=f"entry{i}", fields=f))


def test_normalize_fieldkeys():
    """
    Check library with lowercase field keys.
    """

    lib = Library()
    for i, (entry_type, fields) in enumerate(entries.items()):
        f = [Field(key=k, value=v) for k, v in fields.items()]
        lib.add(Entry(entry_type=entry_type, key=f"entry{i}", fields=f))

    lib = NormalizeFieldKeys().transform(lib)

    for key in lib.entries_dict:
        assert lib.entries_dict[key] == ref.entries_dict[key]


def test_normalize_fieldkeys_force_last(caplog):
    """
    Check library with uppercase field keys and duplicate normalized keys.
    """
    lib = Library()
    for i, (entry_type, fields) in enumerate(entries.items()):
        f = [Field(key=k.lower(), value="dummyvalue") for k in fields]
        f += [Field(key=k.upper(), value=v) for k, v in fields.items()]
        lib.add(Entry(entry_type=entry_type, key=f"entry{i}", fields=f))

    lib = NormalizeFieldKeys().transform(lib)
    assert re.match(
        r"(WARNING\s*)([\w\.]*\:\w*\.py\:[0-9]*\s*)(NormalizeFieldKeys)(.*)", caplog.text
    )

    for key in lib.entries_dict:
        assert lib.entries_dict[key] == ref.entries_dict[key]
