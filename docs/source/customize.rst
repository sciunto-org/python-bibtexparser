.. _customizing:

===========
Customizing
===========


.. image:: https://user-images.githubusercontent.com/4815944/193734283-f19f94e8-7986-4acf-b1a3-1d215e297224.png
  :width: 800
  :alt: BibtexParser v2 architecture


The core functionality of bibtexparser is deliberately kept simple:

* Upon parsing, the input string is merely split into different parts (blocks) and corresponding subparts (fields, keys, ...).
* Upon writing, the splitting is reversed and the blocks are joined together again, with few formatting options.

Advanced transformations of blocks, such as sorting, encoding, cross-referencing, etc. are not part of the core functionality,
but can be optionally added to the parse stack by using the corresponding middleware layers:
Middleware layers helper classes providing the functionality take a library object and return a new, transformed version of said library.

Middleware Layers
-----------------

.. code-block:: python

    import bibtexparser.middlewares as m

    # We want to add three new middleware layers to our parse stack:
    layers = [
        m.MonthIntMiddleware(), # Months should be represented as int (0-12)
        m.SeparateCoAuthors(), # Co-authors should be separated as list of strings
        m.SplitNameParts() # Individual Names should be split into first, von, last, jr parts
    ]
    library = bibtexparser.parse_file('bibtex.bib', append_middleware=layers)

This example adds three new middleware layers to the parse stack:

1. The first layer converts the month field (which may be represented as String ("February"), native string reference (feb) or integer (2) to the integer representation (0-12).
2. The second layer splits the author field into a list of authors (and similarly for editors, translators, etc.).
3. The third layer splits the author names into a object representing the first, von, last and jr parts of the name.

Default Parse-Stack
^^^^^^^^^^^^^^^^^^^

BibtexParser foresees a default parse stack; i.e., some middleware is automatically applied as we assume it to be
part of the expected functionality for most users.

Currently, the default parse stack consists of the following layers:

* :class:`bibtexparser.middlewares.ResolveStringReferencesMiddleware`: De-Reference reference to @string definitions.
* :class:`bibtexparser.middlewares.RemoveEnclosingMiddleware`: Removes enclosing (e.g. curly braces or "") from values.

The default write stack consists of the following layers:

* :class:`bibtexparser.middlewares.AddEnclosingMiddleware`: Encloses values in curly braces where needed.

When specifying their own stack, user get to chose if they want to add to or overwrite the default stack
by selecting the corresponding argument when calling :code:`bibtexparser.parse` or :code:`bibtexparser.write`:

* :code:`append_middleware`: Add middleware to the default parse stack (similarly :code:`prepend_middleware` for write stack).
* :code:`parse_stack`: Overwrite the default parse stack (similarly :code:`write_stack` for write stack).

.. warning::
    The default parse and write stacks may change on **minor** version updates and between pre-releases.
    To reduce the risk of unnoticed changes in parsing stack, critical applications may want to hard-code
    the full parse stack in their code using :code:`parse_stack` and :code:`write_stack` arguments.

Core Middleware
^^^^^^^^^^^^^^^
The following middleware layers are part of the core functionality of bibtexparser and maintained as part of the main repository.
The functionality is straightforward from the class names, so we will not go into detail here and refer to the
docstrings of the classes instead.

Middleware Layers Regarding Encoding and Enclosing of Values

* :mod:`bibtexparser.middlewares.AddEnclosingMiddleware`
* :mod:`bibtexparser.middlewares.RemoveEnclosingMiddleware`
* :mod:`bibtexparser.middlewares.LatexEncodingMiddleware`
* :mod:`bibtexparser.middlewares.LatexDecodingMiddleware`

Middleware Layers Regarding Value References and Representation

* :mod:`bibtexparser.middlewares.ResolveStringReferencesMiddleware`
* :mod:`bibtexparser.middlewares.MonthIntMiddleware`
* :mod:`bibtexparser.middlewares.MonthAbbreviationMiddleware`
* :mod:`bibtexparser.middlewares.MonthLongStringMiddleware`

Middleware Layers Regarding Names

* :mod:`bibtexparser.middlewares.SeparateCoAuthors`
* :mod:`bibtexparser.middlewares.MergeCoAuthors`
* :mod:`bibtexparser.middlewares.SplitNameParts` (requires SeperateCoAuthors to be applied first)
* :mod:`bibtexparser.middlewares.MergeNameParts`

Sorting Middleware Layers

* :mod:`bibtexparser.middlewares.SortBlocksByTypeAndKeyMiddleware`
* :mod:`bibtexparser.middlewares.SortFieldsAlphabeticallyMiddleware`
* :mod:`bibtexparser.middlewares.SortFieldsCustomMiddleware`

.. note::
    As opposed to bibtexparser v1, the en- and decoding of latex characters is now handled by a third-party library.
    Previously, this part was responsible for much of the code complexity and bugs in bibtexparser,
    and leaving this to an established solution is intended to make the use of bibtexparser much more stable,
    even if it comes at the cost of slightly reduced functionality and performance.
    See the migration docs, if you are migrating from bibtexparser v1.

Community-Provided Middleware
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Aiming to keep the core functionality of bibtexparser simple, we encourage users to provide their own middleware layers
and share them with the community.
We will be happy to provide a list of community-provided middleware layers here, so please let us know if you have written one!

.. note::
    To write your own middleware, simply extend the :class:`bibtexparser.middlewares.BlockMiddleware`
    (for functions working on blocks individually, such as encoding) or :class:`bibtexparser.middlewares.LibraryMiddleware`
    (for library-wide transformations, such as sorting blocks) and implement the superclass methods
    according to the python docstrings. Make sure to check out some core middleware layers for examples.

Metadata Fields
^^^^^^^^^^^^^^^

All blocks have a :code:`metadata` attribute, which is a dictionary of arbitrary middleware-value pairs.
This is intended for middleware layers to store metadata about the transformation made by them,
which in turn can be used by other middleware layers (e.g. to reverse the transformation).

The metadata attribute and its exact specification is still experimental and subject to breaking changes
even within minor/path versions. Even when not experimental anymore, it is not intended to be used by users directly,
and may be changed as needed by the corresponding middleware maintainers.

.. _writing_formatting:

Formatting Options for Writing
------------------------------

Basic formatting options (e.g. indentation, line breaks, etc.) have no influence on the :class:`bibtexparser.bparser.Library`
representation and should not / cannot therefore be specified as middleware layers.
These options are instead specified as arguments to the :code:`bibtexparser.write` function.
Specifically, a user may pass a :class:`bibtexparser.BibtexFormatter` object to the :code:`bibtex_format` argument of :code:`bibtexparser.write`.

.. code-block:: python

    bibtex_format = bibtexparser.BibtexFormat()
    bibtex_format.indent = '    '
    bibtex_format.block_separator = '\n\n'
    bib_str = bibtexparser.write_string(library, bibtex_format=bibtex_format)

A few more options are provided and we refer to the docstrings of :class:`bibtexparser.BibtexFormat` for details.
Note: Sorting of blocks and fields is done with the corresponding middleware, as described above.
