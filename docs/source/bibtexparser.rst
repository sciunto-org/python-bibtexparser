.. _bibtexparser_api:

.. contents::

========
Full API
========

:mod:`bibtexparser` --- High-Level Entrypoints
----------------------------------------------

.. automodule:: bibtexparser
    :members: parse_string, parse_file, write_string, write_file


:mod:`bibtexparser.Library` --- The class containing the parsed library
-----------------------------------------------------------------------

.. autoclass:: bibtexparser.Library
    :members: entries, entries_dict, comments, strings, preambles, blocks, failed_blocks


:mod:`bibtexparser.model` --- The classes used in the library
-------------------------------------------------------------
.. automodule:: bibtexparser.model
    :members: Entry, String, Preamble, Block, ExplicitComment, ImplicitComment, Field,
        ParsingFailedBlock, MiddlewareErrorBlock, DuplicateBlockKeyBlock, DuplicateFieldKeyBlock


:mod:`bibtexparser.middlewares` --- Customizers to transform parsed library
---------------------------------------------------------------------------

.. automodule:: bibtexparser.middlewares
    :members:


:mod:`bibtexparser.BibtexFormat` --- Formatting options for writer
------------------------------------------------------------------

.. autoclass:: bibtexparser.BibtexFormat
    :members:
