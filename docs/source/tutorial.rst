Tutorial
========

Prepare a bibtex
----------------

Prepare a bibtex sample for illustration purpose:

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

Parse
-----

OK. Everything is in place. Let's parse the bibtex.

.. code-block:: python

    from bibtexparser.bparser import BibTexParser

    with open('bibtex.bib') as bibfile:
        bp = BibTexParser(bibfile.read())
        print(bp.get_entry_list())


It prints a list of dictionaries:

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


Customizations
--------------

By default, the parser does not alter the content of each field but there are many cases where this is not usable.
For instance, instead of a string with a list of authors, you can prefer a list.
The library includes several functions which may suit your needs. Otherwise,you can read them to create your own functions.

.. code-block:: python

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

    with open('bibtex.bib', 'r') as bibfile:
        bp = BibTexParser(bibfile.read(), customization=customizations)
        print(bp.get_entry_list())


Accents and weird characters
----------------------------

Your bibtex may content accents and specific characters.
They are sometimes coded like this ``\'{e}`` but this is not the correct way, ``{\'e}`` is prefered. Moreover, you may want to manipulate ``é``. There is different situations:

* Case 1: you plan to use this library to work with latex and you assume that the original bibtex is clean. You have nothing to do.

* Case 2: you plan to use this library to work with latex but your bibtex is not really clean.

.. code-block:: python

    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import homogeneize_latex_encoding

    with open('bibtex.bib', 'r') as bibfile:
        bp = BibTexParser(bibfile.read(), customization=homogeneize_latex_encoding)
        print(bp.get_entry_list())


* Case 3: you plan to use this library to work with something different and your bibtex is not really clean.
  Then, you probably want to use unicode.

.. code-block:: python

    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode

    with open('bibtex.bib', 'r') as bibfile:
        bp = BibTexParser(bibfile.read(), customization=convert_to_unicode)
        print(bp.get_entry_list())


Note: if you want to mix different customization functions, you can write your own function.

Cleaning bibtex tags/field names
--------------------------------

Bibtex tags/field names are always converted to lower case. By default, some field names are also modified, e.g.
authors->author. Disable this behaviour as follows:

.. code-block:: python

    bp = BibTexParser(bibfile.read(), homogenise_fields=False)

Write a bibtex
--------------

After modifications, you can generate a string containing all entries in the bibtex format.

.. code-block:: python

    from bibtexparser.bwriter import to_bibtex

    output = to_bibtex(bp)
