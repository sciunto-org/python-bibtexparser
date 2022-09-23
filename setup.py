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


def load_readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name='bibtexparser',
    version=version,
    url="https://github.com/sciunto-org/python-bibtexparser",
    author="Francois Boulogne and other contributors",
    license="LGPLv3 or BSD",
    author_email="code@mweiss.ch",
    description="Bibtex parser for python 3",
    long_description_content_type="text/x-rst",
    long_description=load_readme(),
    packages=['bibtexparser'],
    install_requires=['pyparsing>=2.0.3'],
)
