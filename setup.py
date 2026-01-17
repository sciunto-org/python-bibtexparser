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
    python_requires=">=3.9",
    packages=setuptools.find_packages(include=["bibtexparser", "bibtexparser.*"]),
    package_data={"bibtexparser": ["py.typed"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pylatexenc~=2.10",
    ],
    extras_require={
        "test": [
            "pytest",  # Test runner
            "pytest-xdist",  # Parallel tests: `pytest -n <num-workers>`
            "pytest-cov",  # Code coverage
            "jupyter",  # For runnable examples
        ],
        "docs": [
            "sphinx",
        ],
    },
)
