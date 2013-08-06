.. BibtexParser documentation master file, created by
   sphinx-quickstart on Thu Aug  1 13:30:23 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BibtexParser's documentation!
========================================





:Author: François Boulogne
:Download: `Stable version <http://source.sciunto.org/>`_
:Developer's corner: `github.com project <https://github.com/sciunto/python-bibtexparser>`_
:Generated: |today|
:License: AGPL v3
:Version: |release|


Contents:

.. toctree::
    :maxdepth: 2

    install.rst
    bibtexparser.rst


.. code-block:: python
    # Prepare a bibtex sample
    # for illustration purpose

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

    # OK. Everything is in place.
    # Let's parse the bibtex.

    from bibtexparser.bparser import BibTexParser

    with open('bibtex.bib', 'r') as bibfile:
        bp = BibTexParser(bibfile)
        print(bp.get_entry_list())

    # You get
    # [{'journal': 'Nice Journal', 'comments': 'A comment', 'pages': '12--23', 'month': 'jan', 'abstract': 'This is an abstract. This line should be long enough to test\nmultilines...', 'title': 'An amazing title', 'year': '2013', 'volume': '12', 'id': 'Cesar2013', 'author': 'Jean César', 'keyword': 'keyword1, keyword2', 'type': 'article'}]



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

