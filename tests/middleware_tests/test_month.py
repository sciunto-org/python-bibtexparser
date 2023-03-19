from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.month import MonthLongStringMiddleware, MonthAbbreviationMiddleware, MonthIntMiddleware
from bibtexparser.splitter import Splitter

test_bibtex_string = """
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

@article{smith2021,
    author  = "Smith, J.",
    title   = "A Test Article",
    journal = "J. of Testing",
    month   = "November",
    year    = "2021"
}
"""


def test_long_string_months():
    original_library = Splitter(test_bibtex_string).split()

    new_library = MonthLongStringMiddleware(allow_inplace_modification=False).transform(original_library)

    assert new_library.entries_dict["smith2022"]["month"] == '"jan"', "enclosed values should not be not changed"
    assert new_library.entries_dict["doe2021"]["month"] == "April"
    assert new_library.entries_dict["jones2023"]["month"] == "August"
    assert new_library.entries_dict["smith2021"]["month"] == '"November"', "enclosed values should not be not changed"

    # Test the same after enclosing is removed
    no_enclosing_library = RemoveEnclosingMiddleware(allow_inplace_modification=False).transform(original_library)
    new_library = MonthLongStringMiddleware(allow_inplace_modification=False).transform(no_enclosing_library)

    assert new_library.entries_dict["smith2022"]["month"] == "January"
    assert new_library.entries_dict["doe2021"]["month"] == "April"
    assert new_library.entries_dict["jones2023"]["month"] == "August"
    assert new_library.entries_dict["smith2021"]["month"] == "November"


def test_short_string_months():
    original_library = Splitter(test_bibtex_string).split()

    new_library = MonthAbbreviationMiddleware(allow_inplace_modification=False).transform(original_library)

    assert new_library.entries_dict["smith2022"]["month"] == '"jan"', "enclosed values should not be not changed"
    assert new_library.entries_dict["doe2021"]["month"] == "apr"
    assert new_library.entries_dict["jones2023"]["month"] == "aug"
    assert new_library.entries_dict["smith2021"]["month"] == '"November"', "enclosed values should not be not changed"

    # Test the same after enclosing is removed
    no_enclosing_library = RemoveEnclosingMiddleware(allow_inplace_modification=False).transform(original_library)
    new_library = MonthAbbreviationMiddleware(allow_inplace_modification=False).transform(no_enclosing_library)

    assert new_library.entries_dict["smith2022"]["month"] == "jan"
    assert new_library.entries_dict["doe2021"]["month"] == "apr"
    assert new_library.entries_dict["jones2023"]["month"] == "aug"
    assert new_library.entries_dict["smith2021"]["month"] == "nov"



def test_int_months():
    original_library = Splitter(test_bibtex_string).split()

    new_library = MonthIntMiddleware(allow_inplace_modification=False).transform(original_library)

    assert new_library.entries_dict["smith2022"]["month"] == '"jan"', "enclosed values should not be not changed"
    assert new_library.entries_dict["doe2021"]["month"] == 4
    assert new_library.entries_dict["jones2023"]["month"] == 8
    assert new_library.entries_dict["smith2021"]["month"] == '"November"', "enclosed values should not be not changed"

    # Test the same after enclosing is removed
    no_enclosing_library = RemoveEnclosingMiddleware(allow_inplace_modification=False).transform(original_library)
    new_library = MonthIntMiddleware(allow_inplace_modification=False).transform(no_enclosing_library)

    assert new_library.entries_dict["smith2022"]["month"] == 1
    assert new_library.entries_dict["doe2021"]["month"] == 4
    assert new_library.entries_dict["jones2023"]["month"] == 8
    assert new_library.entries_dict["smith2021"]["month"] == 11
