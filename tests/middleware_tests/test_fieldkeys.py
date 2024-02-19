from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.fieldkeys import NormalizeFieldKeys
from bibtexparser.splitter import Splitter

test_bibtex_string_lowercasekeys = """
@article{smith2022,
  author  = "Smith, J.",
  title   = "A Test Article",
  journal = "J. of Testing",
  month   = "jan",
  year    = "2022"
}

@book{doe2021,
  author    = "Doe, J.",
  title     = "A Test Book",
  publisher = "Test Pub.",
  year      = "2021",
  month     = apr
}

@inproceedings{jones2023,
  author    = "Jones, R.",
  title     = "A Test Conf. Paper",
  booktitle = "Proc. of the Intl. Test Conf.",
  year      = "2023",
  month     = 8
}
"""

test_bibtex_string_capitalizedkeys = """
@article{smith2022,
  Author  = "Smith, J.",
  Title   = "A Test Article",
  Journal = "J. of Testing",
  Month   = "jan",
  Year    = "2022"
}

@book{doe2021,
  Author    = "Doe, J.",
  Title     = "A Test Book",
  Publisher = "Test Pub.",
  Year      = "2021",
  Month     = apr
}

@inproceedings{jones2023,
  Author    = "Jones, R.",
  Title     = "A Test Conf. Paper",
  Booktitle = "Proc. of the Intl. Test Conf.",
  Year      = "2023",
  Month     = 8
}
"""

def test_normalize_lowercase():
    original_library = Splitter(test_bibtex_string_lowercasekeys).split()

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
    original_library = Splitter(test_bibtex_string_capitalizedkeys).split()

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
