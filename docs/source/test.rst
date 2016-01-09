How to run the test suite?
==========================

This page briefly describes how to run the test suite.
This is useful for contributors, for packagers but also for users who wants to check their environment.


Virtualenv
----------

You can make a virtualenv. I like `pew <https://pypi.python.org/pypi/pew/>`_ for that because the API is easier.

The first time, you need to make a virtualenv

.. code-block:: sh

    pew mkproject bibtexparser
    pip install -r requirements.txt
    python setup.py install
    nosetest


If you already have a virtualenv, you can use workon

.. code-block:: sh

    pew workon bibtexparser


Tox
---

The advantage of `Tox <https://pypi.python.org/pypi/tox>`_ is that you can build and test the code against several versions of python.
Of course, you need tox to be installed on your system.
The configuration file is tox.ini, in the root of the project. There, you can change the python versions.

.. code-block:: sh

    tox # and nothing more :)
