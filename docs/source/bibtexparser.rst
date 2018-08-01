.. _bibtexparser_api:

.. contents::

bibtexparser: API
=================

:mod:`bibtexparser` --- Parsing and writing BibTeX files
--------------------------------------------------------

.. automodule:: bibtexparser
    :members: load, loads, dumps, dump

:mod:`bibtexparser.bibdatabase` --- The bibliographic database object
---------------------------------------------------------------------

.. autoclass:: bibtexparser.bibdatabase.BibDatabase
    :members: entries, entries_dict, comments, strings, preambles

:mod:`bibtexparser.bparser` --- Tune the default parser
--------------------------------------------------------

.. automodule:: bibtexparser.bparser
    :members:

:mod:`bibtexparser.customization` --- Functions to customize records
--------------------------------------------------------------------

.. automodule:: bibtexparser.customization
    :members:

Exception classes
^^^^^^^^^^^^^^^^^
.. autoclass:: bibtexparser.customization.InvalidName

:mod:`bibtexparser.bwriter` --- Tune the default writer
-------------------------------------------------------

.. autoclass:: bibtexparser.bwriter.BibTexWriter
    :members:

:mod:`bibtexparser.bibtexexpression` --- Parser's core relying on pyparsing
---------------------------------------------------------------------------

.. automodule:: bibtexparser.bibtexexpression
    :members:

