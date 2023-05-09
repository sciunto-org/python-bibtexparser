========================
Migrating from v1 to v2
========================

Before you start migrating, we recommend you read the docs regarding the terminology and architecture of bibtexparser v2,
and have a quick look at the tutorial to get a feeling for the new API.

Status of `v2`
--------------

The `v2` branch is well tested and reasonably stable, but it is not yet widely adopted - as an early adopter, y
you may encounter some bugs. If you do, please report them on the issue tracker.
Also, note that some interfaces may change sightly before we release v2.0.0 as stable.

Some customizations from `v1` are not implemented in `v2`, as we doubt they are widely used. If you need one of
these features, please let us know on the issue tracker.


Differences between v1 and v2
-----------------------------

From a user perspective `v2` has the following advantages over `v1`:

* Order of magnitudes faster
* Easily customizable parsing and writing
* Access to more information, such as raw, unparsed bibtex.
* Fault-Tolerant: Able to parse files with syntax errors
* Massively simplified, robuster handling of de- and encoding (special chars, ...).
* Permissive MIT license

Implementation-wise, the main difference of `v2` is that it does not depend on `pyparsing` anymore.
Also, it does not implement any en-/decoding of special characters, but relies on external libraries for this.

To implement these changes, we had to make some breaking changes to the API. Amongst others, be aware that:
* The used vocabulary has slightly changed (TODO link).
* The parameters of the library entrypoint have changed (TODO link).
* `bibtexparser.customizations` is gone, and has been replaced by `bibtexparser.middleware`, which are a bit different in their use. (TODO Link)

Minimal Migration Guide
-----------------------

The following code snippets show how to migrate from `v1` to `v2` for the most common use cases.
It aims to provide the quickest way to get `v1` code running with `v2`.
As such, it makes reduced use of the new features of `v2` and makes use of backwards compatibility APIs where possible.

Changing the entrypoint
~~~~~~~~~~~~~~~~~~~~~~~
TODO

Customizing the parser
~~~~~~~~~~~~~~~~~~~~~~
TODO

Accessing the library
~~~~~~~~~~~~~~~~~~~~~
TODO

Writing a bibtex file (possibly with customizations)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO
