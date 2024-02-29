===================
Migrating: v1 -> v2
===================

Before you start migrating, we recommend you read the docs regarding the terminology and architecture of bibtexparser v2,
and have a quick look at the tutorial to get a feeling for the new API.

Status of v2
------------

The v2 branch is well tested and reasonably stable, but it is not yet widely adopted - as an early adopter,
you may encounter some bugs. If you do, please report them on the issue tracker.
Also, note that some interfaces may change sightly before we release v2.0.0 as stable.

Some customizations from v1 are not implemented in v2, as we doubt they are widely used. If you need one of
these features, please let us know on the issue tracker.


Differences between v1 and v2
-----------------------------

From a user perspective v2 has the following advantages over v1:

* Order of magnitudes faster
* Easily customizable parsing and writing
* Access to more information, such as raw, unparsed bibtex.
* Fault-Tolerant: Able to parse files with syntax errors
* Robuster handling of de- and encoding (special chars, ...).
* Permissive MIT license

Implementation-wise, the main difference of v2 is that it does not depend on ``pyparsing`` anymore.
Also, it does not implement any en-/decoding of special characters, but relies on external libraries for this.

To implement these changes, we had to make some breaking changes to the API. Amongst others, be aware that:

* The used vocabulary has slightly changed. [:ref:`docs <vocab>`]
* The primary entrypoints have changed. [:ref:`docs <entrypoint>`]
* The module ``bibtexparser.customizations`` been replaced by the module ``bibtexparser.middleware`` [:ref:`docs <customizing>`]

Minimal Migration Guide (without customizations)
------------------------------------------------

The following code snippets show how to migrate from v1 to v2 for the most common use cases.
It aims to provide the quickest way to get v1 code running with v2.
As such, it makes reduced use of the new features of v2 and makes use of backwards compatibility APIs where possible.

.. warning:: This migration guide is not complete. It covers the parts which are presumably the trickiest ones to migrate.
                Further migration steps should be needed, but should either be trivial or very specific to your use case
                (in the latter case you may want to use at the :ref:`customization <customizing>` docs).

Changing the entrypoint with default settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make sure that users dont "migrate by accident" to bibtex v2, we changed the entrypoint of the package:

.. code-block:: python

    # v1
    import bibtexparser
    with open('bibtex.bib') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    # v2
    import bibtexparser
    library = bibtexparser.parse_file(bibtex_file)


For most usecases, these default settings should be sufficient, even though there are differences in
the default configurations between v1 and v2 and thus the outcome you will see.
Read the :ref:`customization docs <customizing>` for instruction on how to customize the parsing behavior.


Accessing the library
~~~~~~~~~~~~~~~~~~~~~

While in v1 entries were represented as dicts, in v2 they are represented as ``Entry`` objects.

.. code-block:: python

    # v1
    for entry in bib_database.entries:
        print(entry['title'])

    # v2
    for entry in library.entries:
        # ... the new 'typed' way to access fields values ...
        print(entry.fields_dict['title'].value)
        # ... but to facilitate migration or simple cases, this shorthand notation also works ...
        print(entry['title'])


Similarly, other block types (comments, strings, ...) are now also represented as dedicated :ref:`object types <vocab>`,
but for them, the migration is straight forward and we will not go into detail here.

.. note::

    Working with the actual field instances (``entry.fields`` or ``entry.fields_dict``) and not the shorthand notation
    (``entry[field_key]``) makes additional information (e.g. raw bibtex or start line of the field in the parsed file) available.
    We recommend you check out the new data types and their attributes.


Writing a bibtex file (possibly with customizations)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The way to write a bibtex file has changed fundamentally in v2, and is now handeled in a fashion very similar to the parsing.
See the :ref:`writing quickstart <writing_quickstart>` and :ref:`writing formatting <writing_formatting>` for more information.
