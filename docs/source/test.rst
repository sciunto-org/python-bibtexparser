How to test?
============

This page briefly describes how to run the test suite.
This is useful for contributors but also for packagers.


Virtualenv
----------

You can make a virtualenv. I like `pew <https://pypi.python.org/pypi/pew/>`_ for that because the API easier.

The first time, you need to make a virtualenv

.. code-block:: sh

    pew mkproject bibtexparser
    python setup.py install
    nosetest


If you already have a virtualenv

.. code-block:: sh

    pew workon bibtexparser
    python setup.py install
    nosetest


Tox
---

The advantage of `Tox <https://pypi.python.org/pypi/tox>`_ is that you can build and test the code against several versions of python.
Of course, you need tox to be installed on your system.
The configuration file is tox.ini, in the root of the project.

.. code-block:: sh

    tox # and nothing more :)
