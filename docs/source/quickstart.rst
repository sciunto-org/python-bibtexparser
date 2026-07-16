==========
Quickstart
==========

This section provides a TLDR-style overview of the high-level features of bibtexparser.
For more detailed information, please refer to the corresponding sections of the documentation.

.. _vocab:

Prerequisite: Vocabulary
========================

* An **entry** refers to a citable item, e.g. ``@book{...}``, ``@article{...}``, etc.
* A **preamble** is a ``@preamble{...}`` block.
* A **string** is ``@string{...}``.
* An **explicit comment** is written as ``@comment{...}``.
* An **implicit comment** is any text not within any ``@...{...}`` block.
* Each of the above is called a **block**, i.e., any .bib file is a collection of blocks of the above types.

In an entry, you can find

* an **entry type** like ``article``, ``book``, etc.
* an **entry key**, e.g. ``Cesar2013`` in ``@article{Cesar2013, ...}``.
* and **fields**, which are the key-value pairs in the entry, e.g. ``author = {Jean César}``.
* each field has a **field key** and a **field value**.


Step 1: Parsing with Defaults
=============================

First, we prepare a BibTeX sample file. This is just for the purpose of illustration:

.. code-block:: python

    bibtex_str = """
    @comment{
        This is my example comment.
    }

    @ARTICLE{Cesar2013,
      author = {Jean César},
      title = {An amazing title},
      year = {2013},
      volume = {12},
      pages = {12--23},
      journal = {Nice Journal}
    }
    """



Let's attempt to parse this string using the default bibtexparser configuration:

.. _entrypoint:

.. code-block:: python

    import bibtexparser
    library = bibtexparser.parse_string(bibtex_str) # or bibtexparser.parse_file("my_file.bib")


The returned ``library`` object provides access to the parsed blocks, i.e., parsed high-level segments of the bibtex such as entries, comments, strings and preambles.
You can access them by type, or iterate over all blocks, as shown below:

.. code-block:: python

    print(f"Parsed {len(library.blocks)} blocks, including:"
      f"\n\t{len(library.entries)} entries"
        f"\n\t{len(library.comments)} comments"
        f"\n\t{len(library.strings)} strings and"
        f"\n\t{len(library.preambles)} preambles")

    # Output:
    # Parsed 2 blocks, including:
    #   1 entries
    #   1 comments
    #   0 strings and
    #   0 preambles


As you can see, the parsed blocks are represented as dedicated object types (entries, strings, preambles and comments).
They share some supertype attributes (e.g. they provide access to their raw bibtex representation and their start line in the file),
but primarily expose attributes specific to their type (e.g. entries provide access to their key, type and fields).

Example of exposed attributes:

.. code-block:: python

    # Comments have just one specific attribute
    first_comment = library.comments[0]
    first_comment.comment # The comment string

    # Entries have more attributes
    first_entry = library.entries[0]
    first_entry.key # The entry key
    first_entry.entry_type # The entry type, e.g. "article"
    first_entry.fields # The entry fields (e.g. author, title, etc. with their values)
    first_entry.fields_dict # The entry fields, as a dictionary by field key

    # Each field of the entry is a `bibtexparser.model.Field` instance
    first_field = first_entry.fields[0]
    first_field.key # The field key, e.g. "author"
    first_field.value # The field value, e.g. "Albert Einstein and Boris Johnson"

For a list of all available attributes, see the documentation of the ``bibtexparser.model`` module.


Step 2: Error Checking
======================

We aim at being as forgiving as possible when parsing BibTeX files:
If the parsing of a block fails, we try to recover and continue parsing the rest of the file.

Failed blocks are still stored in the library,
and you should check for their presence to make sure mistakes are not going undetected.

.. code-block:: python

    if len(library.failed_blocks) > 0:
        print("Some blocks failed to parse. Check the entries of `library.failed_blocks`.")
    else:
        print("All blocks parsed successfully")

Obviously, in your code, you may want to go beyond simply printing a statement
when faced with failed_blocks.
All failed blocks are instances of ``bibtexparser.model.ParsingFailedBlock``
(or one of its subtypes) and expose at least the following attributes to investigate the problem:

.. code-block:: python

    failed_block = library.failed_blocks[0]
    failed_block.error       # The exception describing why parsing failed
    failed_block.start_line  # The line in the file where the block started
    failed_block.raw         # The raw, unparsed bibtex of the block

Depending on the type of failure, a more specific subtype with additional attributes is used:

* ``DuplicateFieldKeyBlock``: The entry contained the same field key more than once
  (e.g. two ``title`` fields). The offending keys are available as ``failed_block.duplicate_keys``.
* ``DuplicateBlockKeyBlock``: The library already contained a block with the same entry key.
  The previously parsed block is available as ``failed_block.previous_block``.
* ``MiddlewareErrorBlock``: A middleware raised an exception while transforming the block.

For these types, the block as parsed before the error was detected is available
as ``failed_block.ignore_error_block``, which you may use to recover from the error
manually (e.g. by fixing and re-adding it to the library) if you choose to do so.

Optional compatibility preflight
--------------------------------

For a new or unusual file, the read-only compatibility preflight exercises the
default parse/write contract without changing the source:

.. code-block:: console

    $ python -m bibtexparser check references.bib
    COMPATIBLE: default bibliography codec checks
      Source coverage: passed
      Parse failures absent: passed
      Semantic round trip: passed
      Canonical output stable: passed
      Output encodable: passed
      Exact source bytes: would change
      Note: default writing would normalize layout, but protected data is stable.

After installation, the equivalent command is ``bibtexparser check
references.bib``. Exit status 0 means compatible, 1 means one or more
compatibility invariants failed, and 2 means the file could not be read. Pass
``--json`` for a machine-readable report.

The same check is available through Python:

.. code-block:: python

    report = bibtexparser.check_file("references.bib")
    if not report.compatible:
        for diagnostic in report.diagnostics:
            print(diagnostic.code, diagnostic.line, diagnostic.message)

The preflight verifies:

* raw block spans cover every non-whitespace part of the source;
* the parser retained no explicit failed blocks;
* writing and reparsing preserve the ordered semantic inventory, including
  field order, field enclosures, and supported comment blocks;
* canonical output reaches a fixed point after the first write; and
* canonical output can be represented in the selected source encoding.

``exact_source_match`` is informational and compares encoded bytes. A false
value is compatible when the only observed effect is permitted canonical
formatting and every required check passes. The report deliberately says which
invariants were checked: using the same parser for the first and second parse
cannot independently prove that every possible input was interpreted correctly.

The thorough preflight is opt-in because it parses twice and writes twice.
Ordinary parsing continues to log detected block failures and exposes them in
``library.failed_blocks`` without paying that additional cost on every read.

On incompatibility, the text and JSON CLI reports include a pre-filled,
privacy-safe GitHub issue-form URL unless ``--no-issue-link`` is supplied. The
URL is only a draft: the command does not open it, perform a network request, or
create an issue. It contains environment and check metadata plus a source hash,
but no file path, bibliography content, or source snippet.

The text report also points to the explicit source-disclosure option:

.. code-block:: console

    $ python -m bibtexparser check references.bib --include-source-in-issue-link

That command keeps the privacy-safe draft and adds a second draft containing an
exact failed block when the checker can extract a bounded reproduction. A
duplicate-key reproduction includes both relevant blocks. The checker does not
truncate an oversized block, because a partial block could be invalid or fail
to reproduce the problem; in that case, add a reviewed minimal example
manually.

The source-bearing URL exposes bibliography content in terminal logs, browser
history, and the GitHub draft even if the issue is never submitted. The command
therefore requires explicit opt-in and prints a warning. Review the URL and the
draft carefully before submitting anything.

.. _writing_quickstart:

Step 3: Exporting with Defaults
===============================

Eventually, you may want to write the parsed BibTeX back to a file or bibtex string.

This can be quickly achieved using the following:

.. code-block:: python

    new_bibtex_str = bibtexparser.write_string(library) # or bibtexparser.write_file("my_new_file.bib", library)
    print(new_bibtex_str)

    # Output:
    # @comment{This is my example comment.}
    #
    #
    # @article{Cesar2013,
    #     author = {Jean César},
    #     title = {An amazing title},
    #     year = {2013},
    #     volume = {12},
    #     pages = {12--23},
    #     journal = {Nice Journal}
    # }

As you can see, the content (besides some white-spacing and other layout) is identical to the original string.
Naturally, the writer can be configured to your needs. For more information on that, see :ref:`the customization documentation <customizing>`.
