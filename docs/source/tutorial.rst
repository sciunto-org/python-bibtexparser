========
Tutorial
========

Step 1: Prepare a BibTeX file
=============================

First, we prepare a BibTeX sample file. This is just for the purpose of illustration:

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

Step 2: Parse it!
=================

Simplest call
-------------

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
      'ID': 'Cesar2013',
      'author': 'Jean César',
      'keyword': 'keyword1, keyword2',
      'ENTRYTYPE': 'article'}]

Note that, by convention, uppercase keys are auto-generated data, while lowercase keys come from the original bibtex file.

Parse a stream
--------------

You don't necessarily have to first read the file and then parse it. You can parse directly a stream like this:

.. code-block:: python

    import bibtexparser

    with open('bibtex.bib') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)


Some options
------------

In the previous snippet, several default options are used.

.. code-block:: python

    import bibtexparser
    from bibtexparser.bparser import BibTexParser

	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	parser.homogenise_fields = False
	parser.common_strings = False
	bib_database = bibtexparser.loads(bibtex_str, parser)


Step 3: Export
==============

Once you worked on your parsed database, you may want to export the result. This library provides some functions to help on that. However, you can write your own functions if you have specific requirements.

Create a BibTeX file or string
--------------------------------

The bibliographic data can be converted back into a BibTeX file like this:

.. code-block:: python

    import bibtexparser

    bibtex_str = bibtexparser.dumps(bib_database)

Using the writer
----------------

In the first section we prepared a BibTeX sample file, we can prepare the same file using pure python and the ``BibTexWriter`` class.

.. code-block:: python

    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    db = BibDatabase()
    db.entries = [
        {'journal': 'Nice Journal',
         'comments': 'A comment',
         'pages': '12--23',
         'month': 'jan',
         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...',
         'title': 'An amazing title',
         'year': '2013',
         'volume': '12',
         'ID': 'Cesar2013',
         'author': 'Jean César',
         'keyword': 'keyword1, keyword2',
         'ENTRYTYPE': 'article'}]

    writer = BibTexWriter()
    with open('bibtex.bib', 'w') as bibfile:
        bibfile.write(writer.write(db))

This code generates the following file:

.. code-block:: latex

    @article{Cesar2013,
     abstract = {This is an abstract. This line should be long enough to test
    multilines...},
     author = {Jean César},
     comments = {A comment},
     journal = {Nice Journal},
     keyword = {keyword1, keyword2},
     month = {jan},
     pages = {12--23},
     title = {An amazing title},
     volume = {12},
     year = {2013}
    }

The writer also has several flags that can be enabled to customize the output file.
For example we can use ``indent`` and ``comma_first`` to customize the previous entry, first the code:

.. code-block:: python

    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    db = BibDatabase()
    db.entries = [
        {'journal': 'Nice Journal',
         'comments': 'A comment',
         'pages': '12--23',
         'month': 'jan',
         'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...',
         'title': 'An amazing title',
         'year': '2013',
         'volume': '12',
         'ID': 'Cesar2013',
         'author': 'Jean César',
         'keyword': 'keyword1, keyword2',
         'ENTRYTYPE': 'article'}]

    writer = BibTexWriter()
    writer.indent = '    '     # indent entries with 4 spaces instead of one
    writer.comma_first = True  # place the comma at the beginning of the line
    with open('bibtex.bib', 'w') as bibfile:
        bibfile.write(writer.write(db))

This code results in the following, customized, file:

.. code-block:: latex

    @article{Cesar2013
    ,    abstract = {This is an abstract. This line should be long enough to test
    multilines...}
    ,    author = {Jean César}
    ,    comments = {A comment}
    ,    journal = {Nice Journal}
    ,    keyword = {keyword1, keyword2}
    ,    month = {jan}
    ,    pages = {12--23}
    ,    title = {An amazing title}
    ,    volume = {12}
    ,    year = {2013}
    }

Another interesting option is the protection of upper case letters.

.. code-block:: python

    writer.protect_upper_case = True


For instance, if the original title has upper case letters or words, the result looks like

.. code-block:: latex
    @article{Cesar2013,
        title = {An {A}mazing title},
        author = {Jean César}
    }


Flags to the writer object can modify not only how an entry is printed but how several BibTeX entries are sorted and separated.
See the :ref:`bibtexparser_api` for the full list of flags.


Step 4: Add salt and pepper
===========================

In this section, we discuss about some customizations and details.

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


If you think that you have a customization which could be useful to others, please share with us!


Accents and weird characters
----------------------------

Your bibtex may content accents and specific characters.
They are sometimes coded like this ``\'{e}`` but this is not the correct way, ``{\'e}`` is prefered. Moreover, you may want to manipulate ``é``. There is different situations:

* Case 1: you plan to use this library to work with latex and you assume that the original bibtex is clean. You have nothing to do.

* Case 2: you plan to use this library to work with latex but your bibtex is not really clean.

.. code-block:: python

    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import homogenize_latex_encoding

    with open('bibtex.bib') as bibtex_file:
        parser = BibTexParser()
        parser.customization = homogenize_latex_encoding
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        print(bib_database.entries)


* Case 3: you plan to use this library to work with something different and your bibtex is not really clean.
  Then, you probably want to use unicode.

.. code-block:: python

    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode

    with open('bibtex.bib') as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        print(bib_database.entries)


.. Note::

    If you want to mix different customization functions, you can write your own function.


