Tutorial
========

Preparing a BibTeX file
-----------------------

Prepare a BibTeX sample file for illustration purpose:

.. code-block:: python

    bibtex = """@ARTICLE{Cesar2013,
      author = {Jean César},
      title = {An amazing title},
      year = {2013},
      month = jan,
      volume = {12},
      pages = {12--23},
      journal = {Nice Journal},
      abstract = {This is an abstract. This line should be long enough to test
    	 multilines...},
      comments = {A comment},
      keywords = {keyword1, keyword2}
    }
    """

    with open('bibtex.bib', 'w') as bibfile:
        bibfile.write(bibtex)

Parsing the file into a bibliographic database object
-----------------------------------------------------

OK. Everything is in place. Let's parse the BibTeX file.

.. code-block:: python

    import bibtexparser

    with open('bibtex.bib') as bibtex_file:
        bibtex_str = bibtex_file.read()

    bib_database = bibtexparser.loads(bibtex_str)
    print(bib_database.entries)


It prints a list of dictionaries for reference entries, for example books, articles:

.. code-block:: python

    [{'journal': 'Nice Journal',
      'comments': 'A comment',
      'pages': '12--23',
      'month': 'jan',
      'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...',
      'title': 'An amazing title',
      'year': '2013',
      'volume': '12',
      'id': 'Cesar2013',
      'author': 'Jean César',
      'keyword': 'keyword1, keyword2',
      'type': 'article'}]



Alternatively, you can parse a file-like object directly like this:

.. code-block:: python

    import bibtexparser

    with open('bibtex.bib') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)


Creating a BibTeX file or string
--------------------------------

The bibliographic data can be converted back into a BibTeX file like this:

.. code-block:: python

    import bibtexparser

    bibtex_str = bibtexparser.dumps(bib_database)


Customizations
--------------

By default, the parser does not alter the content of each field and keeps it as a simple string. There are many cases
where this is not desired. For example, instead of a string with a multiple of authors, it could be parsed as a list.

To modify field values during parsing, a callback function can be supplied to the parser which can be used to modify
BibTeX entries. The library includes several functions which may be used. Alternatively, you can read them to create
your own functions.

.. code-block:: python

    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import *

    # Let's define a function to customize our entries.
    # It takes a record and return this record.
    def customizations(record):
        """Use some functions delivered by the library

        :param record: a record
        :returns: -- customized record
        """
        record = type(record)
        record = author(record)
        record = editor(record)
        record = journal(record)
        record = keyword(record)
        record = link(record)
        record = page_double_hyphen(record)
        record = doi(record)
        return record

    with open('bibtex.bib') as bibtex_file:
        parser = BibTexParser()
        parser.customization = customizations
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        print(bib_database.entries)


Accents and weird characters
----------------------------

Your bibtex may content accents and specific characters.
They are sometimes coded like this ``\'{e}`` but this is not the correct way, ``{\'e}`` is prefered. Moreover, you may want to manipulate ``é``. There is different situations:

* Case 1: you plan to use this library to work with latex and you assume that the original bibtex is clean. You have nothing to do.

* Case 2: you plan to use this library to work with latex but your bibtex is not really clean.

.. code-block:: python

    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import homogeneize_latex_encoding

    with open('bibtex.bib') as bibfile:
        parser = BibTexParser()
        parser.customization = homogeneize_latex_encoding
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        print(bib_database.entries)


* Case 3: you plan to use this library to work with something different and your bibtex is not really clean.
  Then, you probably want to use unicode.

.. code-block:: python

    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode

    with open('bibtex.bib') as bibfile:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        print(bib_database.entries)


Note: if you want to mix different customization functions, you can write your own function.

