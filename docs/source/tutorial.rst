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
      keywords = {keyword1, keyword2},
    }
    """

    with open('bibtex.bib', 'w') as bibfile:
        bibfile.write(bibtex)

Parse
-----

OK. Everything is in place. Let's parse the bibtex.

.. code-block:: python

    from bibtexparser.bparser import BibTexParser

    with open('bibtex.bib', 'r') as bibfile:
        bp = BibTexParser(bibfile)
        print(bp.get_entry_list())


It prints a list of dictionaries:

.. code-block:: sh

    [{'journal': 'Nice Journal', 'comments': 'A comment', 'pages': '12--23', 'month': 'jan', 'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...', 'title': 'An amazing title', 'year': '2013', 'volume': '12', 'id': 'Cesar2013', 'author': 'Jean César', 'keyword': 'keyword1, keyword2', 'type': 'article'}]


Customizations
--------------

.. code-block:: python

    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import *

    # Let's define a function to customize our entries.
    # It takes a record and return this record.
    def customizations(record):
        """Use all functions delivered by the library

        :param record: a record
        :returns: -- customized record
        """
        record = type(record)
        record = author(record)
        record = editor(record)
        record = journal(record)
        record = keyword(record)
        record = link(record)
        record = page(record)
        record = doi(record)
        return record

    with open('bibtex.bib', 'r') as bibfile:
        bp = BibTexParser(bibfile, customization=customizations)
        print(bp.get_entry_list())


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

