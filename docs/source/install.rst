============
Installation
============

Requirements
------------


Bibtexparser's only requirement is a python interpreter which is not yet EOL (currently >= 3.10).

As of version 2.0.0, bibtexparser is a pure-python project (no direct bindings to C libraries).
As such, it should be rather easy to install on any platform.

Installation from PyPI
--------------------------


To install the latest release (v2) using pip:

.. code-block:: sh

    pip install bibtexparser

If you still need v1, e.g. for a legacy project which you don't want to migrate right now,
pin the major version explicitly:

.. code-block:: sh

    pip install bibtexparser~=1.0

Note that v1 is in maintenance mode, has a different API and is not directly compatible with v2.
See the :doc:`migration guide <migrate>` if you are upgrading an existing v1 project.

Installation of current development version
-------------------------------------------

To install the latest version on the main branch (without manually cloning it), run:

.. code-block:: sh

    pip install --no-cache-dir --force-reinstall git+https://github.com/sciunto-org/python-bibtexparser@main


Installation from source
----------------------------

Download the source from `Github <https://github.com/sciunto-org/python-bibtexparser/>`_.
Navigate to the root of the project and run the following command:

.. code-block:: sh

    pip install .

Or, if you want to install dev dependencies:

.. code-block:: sh

    pip install .[test,lint,docs]
