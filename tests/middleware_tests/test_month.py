import bibtexparser
from bibtexparser.middlewares.enclosing import RemoveEnclosingMiddleware
from bibtexparser.middlewares.month import MonthAbbreviationMiddleware
from bibtexparser.middlewares.month import MonthIntMiddleware
from bibtexparser.middlewares.month import MonthLongStringMiddleware
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

    new_library = MonthLongStringMiddleware(allow_inplace_modification=False).transform(
        original_library
    )

    assert (
        new_library.entries_dict["smith2022"]["month"] == '"jan"'
    ), "enclosed values should not be not changed"
    assert new_library.entries_dict["doe2021"]["month"] == "April"
    assert new_library.entries_dict["jones2023"]["month"] == "August"
    assert (
        new_library.entries_dict["smith2021"]["month"] == '"November"'
    ), "enclosed values should not be not changed"

    # Test the same after enclosing is removed
    m = RemoveEnclosingMiddleware(allow_inplace_modification=False)
    no_enclosing_library = m.transform(original_library)
    m = MonthLongStringMiddleware(allow_inplace_modification=False)
    new_library = m.transform(no_enclosing_library)

    assert new_library.entries_dict["smith2022"]["month"] == "January"
    assert new_library.entries_dict["doe2021"]["month"] == "April"
    assert new_library.entries_dict["jones2023"]["month"] == "August"
    assert new_library.entries_dict["smith2021"]["month"] == "November"


def test_short_string_months():
    original_library = Splitter(test_bibtex_string).split()

    m = MonthAbbreviationMiddleware(allow_inplace_modification=False)
    new_library = m.transform(original_library)

    assert (
        new_library.entries_dict["smith2022"]["month"] == '"jan"'
    ), "enclosed values should not be not changed"
    assert new_library.entries_dict["doe2021"]["month"] == "apr"
    assert new_library.entries_dict["jones2023"]["month"] == "aug"
    assert (
        new_library.entries_dict["smith2021"]["month"] == '"November"'
    ), "enclosed values should not be not changed"

    # Test the same after enclosing is removed
    m = RemoveEnclosingMiddleware(allow_inplace_modification=False)
    no_enclosing_library = m.transform(original_library)
    m = MonthAbbreviationMiddleware(allow_inplace_modification=False)
    new_library = m.transform(no_enclosing_library)

    assert new_library.entries_dict["smith2022"]["month"] == "jan"
    assert new_library.entries_dict["doe2021"]["month"] == "apr"
    assert new_library.entries_dict["jones2023"]["month"] == "aug"
    assert new_library.entries_dict["smith2021"]["month"] == "nov"


def test_int_months():
    original_library = Splitter(test_bibtex_string).split()

    m = MonthIntMiddleware(allow_inplace_modification=False)
    new_library = m.transform(original_library)

    assert (
        new_library.entries_dict["smith2022"]["month"] == '"jan"'
    ), "enclosed values should not be not changed"
    assert new_library.entries_dict["doe2021"]["month"] == 4
    assert new_library.entries_dict["jones2023"]["month"] == 8
    assert (
        new_library.entries_dict["smith2021"]["month"] == '"November"'
    ), "enclosed values should not be not changed"

    # Test the same after enclosing is removed
    m = RemoveEnclosingMiddleware(allow_inplace_modification=False)
    no_enclosing_library = m.transform(original_library)
    m = MonthIntMiddleware(allow_inplace_modification=False)
    new_library = m.transform(no_enclosing_library)

    assert new_library.entries_dict["smith2022"]["month"] == 1
    assert new_library.entries_dict["doe2021"]["month"] == 4
    assert new_library.entries_dict["jones2023"]["month"] == 8
    assert new_library.entries_dict["smith2021"]["month"] == 11


def test_abbreviation_months_set_no_enclosing_demand():
    library = Splitter(test_bibtex_string).split()
    library = RemoveEnclosingMiddleware(allow_inplace_modification=True).transform(library)
    library = MonthAbbreviationMiddleware(allow_inplace_modification=True).transform(library)

    # Month macros (e.g. `jan`) must not be enclosed when writing (see issue #447)
    for key in ("smith2022", "doe2021", "jones2023", "smith2021"):
        assert library.entries_dict[key].fields_dict["month"].enclosing == "no-enclosing"


def test_abbreviation_months_no_demand_on_enclosed_values():
    library = Splitter(test_bibtex_string).split()
    library = MonthAbbreviationMiddleware(allow_inplace_modification=True).transform(library)

    # Still-enclosed (and thus untransformed) values get no demand
    assert library.entries_dict["smith2022"].fields_dict["month"].enclosing is None
    assert library.entries_dict["smith2021"].fields_dict["month"].enclosing is None
    # Unenclosed values were transformed to macros and demand no enclosing
    assert library.entries_dict["doe2021"].fields_dict["month"].enclosing == "no-enclosing"
    assert library.entries_dict["jones2023"].fields_dict["month"].enclosing == "no-enclosing"


def test_int_months_set_no_enclosing_demand():
    library = Splitter(test_bibtex_string).split()
    library = RemoveEnclosingMiddleware(allow_inplace_modification=True).transform(library)
    library = MonthIntMiddleware(allow_inplace_modification=True).transform(library)

    for key in ("smith2022", "doe2021", "jones2023", "smith2021"):
        assert library.entries_dict[key].fields_dict["month"].enclosing == "no-enclosing"


def test_long_string_months_set_no_demand():
    library = Splitter(test_bibtex_string).split()
    library = RemoveEnclosingMiddleware(allow_inplace_modification=True).transform(library)
    library = MonthLongStringMiddleware(allow_inplace_modification=True).transform(library)

    # Full month names are literals (not macros) and should be enclosed as usual
    for key in ("smith2022", "doe2021", "jones2023", "smith2021"):
        assert library.entries_dict[key].fields_dict["month"].enclosing is None


def test_issue_447_month_macro_not_enclosed_when_writing():
    """Months written as bibtex macros (e.g. `jan`) must remain unenclosed.

    See https://github.com/sciunto-org/python-bibtexparser/issues/447
    """
    library = bibtexparser.parse_string("@article{test447,\n month = {1},\n year = {2019}\n}")
    written = bibtexparser.write_string(
        library, prepend_middleware=[MonthAbbreviationMiddleware()]
    )
    assert "month = jan" in written
    # Other values are still enclosed with the default enclosing
    assert "year = {2019}" in written


def test_int_month_not_enclosed_when_writing():
    library = bibtexparser.parse_string("@article{test447,\n month = {jan}\n}")
    written = bibtexparser.write_string(library, prepend_middleware=[MonthIntMiddleware()])
    assert "month = 1" in written
