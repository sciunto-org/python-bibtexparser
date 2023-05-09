==========
Quickstart
==========

This section provides a TLDR-style overview of the high-level features of bibtexparser.
For more detailed information, please refer to the corresponding sections of the documentation.

Prerequisite: Vocabulary
========================

* An **entry** designates for example `@book{...}`, `@article{...}`, etc.
* A **preamble** is a `@preamble{...}` block.
* A **string** is `@string{...}`.
* An **explicit comment** is written as `@comment{...}`.
* An **implicit comment** is any collection of lines not within any `@...{...}` block.
* Each of the above is called a **block**, i.e., any .bib file is a collection of blocks of the above types.

In an entry, you can find

* an **entry type** like `article`, `book`, etc.
* and **entry key**, e.g. `Cesar2013` in `@article{Cesar2013, ...}`.
* and **fields**, which are the key-value pairs in the entry, e.g. `author = {Jean César}`.
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


.. code-block:: python

    import bibtexparser
    library = bibtexparser.parse_string(bibtex_str) # or bibtexparser.parse_file("my_file.bib")


The returned `library` object provides access to the parsed blocks, i.e., parsed high-level segments of the bibtex such as entries, comments, strings and preambles.
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
    first_entry.entry_type # The entry type
    first_entry.fields # The entry fields (e.g. author, title, etc. with their values)
    first_entry.fields_dict # The entry fields, as a dictionary by field key

    # Each field of the entry is a `bibtexparser.model.Field` instance
    first_field = first_entry.fields[0]
    first_field.key # The field key
    first_field.value # The field value

For a list of all available attributes, see the documentation of the `bibtexparser.model` module.


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
Here, the actual failed blocks provided in `library.failed_blocks`
will provide you some more information
(exceeding this tutorial, see the corresponding section of the docs for more detail).

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
Same as the parser, the writer can be configured to your needs, but also by creating a custom writer instance.
For a detailed description of the writer, see the corresponding section of the docs.