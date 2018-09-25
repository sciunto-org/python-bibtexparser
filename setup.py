#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError as ex:
    print('[python-bibtexparser] setuptools not found. Falling back to distutils.core')
    from distutils.core import setup

with open('bibtexparser/__init__.py') as fh:
    for line in fh:
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

setup(
    name         = 'bibtexparser',
    version      = version,
    url          = "https://github.com/sciunto-org/python-bibtexparser",
    author       = "Francois Boulogne and other contributors",
    license      = "LGPLv3 or BSD",
    author_email = "devel@sciunto.org",
    description  = "Bibtex parser for python 2.7 and 3.3 and newer",
    packages     = ['bibtexparser'],
    install_requires = ['pyparsing>=2.0.3',
                        'future>=0.16.0'],
    extra_requires = {'unittest': 'unittest2>=1.1.0'}
)
