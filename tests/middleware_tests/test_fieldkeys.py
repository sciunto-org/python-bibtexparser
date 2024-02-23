from bibtexparser import Library
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.fieldkeys import NormalizeFieldKeys
from bibtexparser.model import Entry, Field

test_entry_1a = Entry(entry_type="article",
                      key="smith2022",
                      fields=[Field(key="author", value='"Smith, J."'),
                              Field(key="title", value='"A Test Article"'),
                              Field(key="journal", value='"J. of Testing"'),
                              Field(key="month", value='"jan"'),
                              Field(key="year", value='"2022"')])
test_entry_2a = Entry(entry_type="book",
                      key="doe2021",
                      fields=[Field(key="author", value='"Doe, J."'),
                              Field(key="title", value='"A Test Book"'),
                              Field(key="publisher", value='"Test Pub."'),
                              Field(key="year", value='"2021"'),
                              Field(key="month", value='apr')])
test_entry_3a = Entry(entry_type="inproceedings",
                      key="jones2023",
                      fields=[Field(key="author", value='"Jones, R."'),
                              Field(key="title", value='"A Test Conf. Paper"'),
                              Field(key="booktitle", value='"Proc. of the Intl. Test Conf."'),
                              Field(key="year", value='"2023"'),
                              Field(key="month", value='8')])
test_library_lowercasekeys = Library()
test_library_lowercasekeys.add(test_entry_1a)
test_library_lowercasekeys.add(test_entry_2a)
test_library_lowercasekeys.add(test_entry_3a)

test_entry_1b = Entry(entry_type="article",
                      key="smith2022",
                      fields=[Field(key="author", value='"Smith, J."'),
                              Field(key="title", value='"A Test Article"'),
                              Field(key="journal", value='"J. of Testing"'),
                              Field(key="month", value='"jan"'),
                              Field(key="year", value='"2022"')])
test_entry_2b = Entry(entry_type="book",
                      key="doe2021",
                      fields=[Field(key="author", value='"Doe, J."'),
                              Field(key="title", value='"A Test Book"'),
                              Field(key="publisher", value='"Test Pub."'),
                              Field(key="year", value='"2021"'),
                              Field(key="month", value='apr')])
test_entry_3b = Entry(entry_type="inproceedings",
                      key="jones2023",
                      fields=[Field(key="author", value='"Jones, R."'),
                              Field(key="title", value='"A Test Conf. Paper"'),
                              Field(key="booktitle", value='"Proc. of the Intl. Test Conf."'),
                              Field(key="year", value='"2023"'),
                              Field(key="month", value='8')])
test_library_capitalizedkeys = Library()
test_library_capitalizedkeys.add(test_entry_1b)
test_library_capitalizedkeys.add(test_entry_2b)
test_library_capitalizedkeys.add(test_entry_3b)


def test_normalize_lowercase():
    original_library = test_library_lowercasekeys
    new_library = NormalizeFieldKeys(allow_inplace_modification=False).transform(
        original_library
    )

    assert "author" in new_library.entries_dict["smith2022"]
    assert new_library.entries_dict["smith2022"]["author"] == '"Smith, J."'
    assert "author" in new_library.entries_dict["doe2021"]
    assert new_library.entries_dict["doe2021"]["author"] == '"Doe, J."'
    assert "author" in new_library.entries_dict["jones2023"]
    assert new_library.entries_dict["jones2023"]["author"] == '"Jones, R."'

    # Test the same after enclosing is removed
    no_enclosing_library = RemoveEnclosingMiddleware(
        allow_inplace_modification=False
    ).transform(original_library)
    new_library = NormalizeFieldKeys(allow_inplace_modification=False).transform(
        no_enclosing_library
    )

    assert "author" in new_library.entries_dict["smith2022"]
    assert new_library.entries_dict["smith2022"]["author"] == "Smith, J."
    assert "author" in new_library.entries_dict["doe2021"]
    assert new_library.entries_dict["doe2021"]["author"] == "Doe, J."
    assert "author" in new_library.entries_dict["jones2023"]
    assert new_library.entries_dict["jones2023"]["author"] == "Jones, R."

def test_normalize_capitalized():
    original_library = test_library_capitalizedkeys
    new_library = NormalizeFieldKeys(allow_inplace_modification=False).transform(
        original_library
    )

    assert "author" in new_library.entries_dict["smith2022"]
    assert new_library.entries_dict["smith2022"]["author"] == '"Smith, J."'
    assert "author" in new_library.entries_dict["doe2021"]
    assert new_library.entries_dict["doe2021"]["author"] == '"Doe, J."'
    assert "author" in new_library.entries_dict["jones2023"]
    assert new_library.entries_dict["jones2023"]["author"] == '"Jones, R."'

    # Test the same after enclosing is removed
    no_enclosing_library = RemoveEnclosingMiddleware(
        allow_inplace_modification=False
    ).transform(original_library)
    new_library = NormalizeFieldKeys(allow_inplace_modification=False).transform(
        no_enclosing_library
    )

    assert "author" in new_library.entries_dict["smith2022"]
    assert new_library.entries_dict["smith2022"]["author"] == "Smith, J."
    assert "author" in new_library.entries_dict["doe2021"]
    assert new_library.entries_dict["doe2021"]["author"] == "Doe, J."
    assert "author" in new_library.entries_dict["jones2023"]
    assert new_library.entries_dict["jones2023"]["author"] == "Jones, R."
