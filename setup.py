#!/usr/bin/env python
import setuptools

version = None

with open("bibtexparser/__init__.py") as fh:
    for line in fh:
        if line.startswith("__version__"):
            version = line.strip().split()[-1][1:-1]
            break
    if not version:
        raise RuntimeError("Could not determine version")


def load_readme():
    with open("README.md") as f:
        return f.read()


setuptools.setup(
    name="bibtexparser",
    version=version,
    url="https://github.com/sciunto-org/python-bibtexparser",
    author="Michael Weiss and other contributors",
    maintainer="Michael Weiss",
    license="MIT",
    author_email="code@mweiss.ch",
    maintainer_email="code@mweiss.ch",
    description="Bibtex parser for python 3",
    long_description_content_type="text/markdown",
    long_description=load_readme(),
    packages=setuptools.find_packages(include=["bibtexparser", "bibtexparser.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pylatexenc>=2.10",
    ],
    extras_require={
        "test": [
            "pytest",  # Test runner
            "pytest-xdist",  # Parallel tests: `pytest -n <num-workers>`
            "pytest-cov",  # Code coverage
            "jupyter",  # For runnable examples
        ],
        "lint": [
            "black==23.3.0",
            "isort==5.12.0",
            "docstr-coverage==2.2.0",
        ],
        "docs": [
            "sphinx",
        ],
    },
)
