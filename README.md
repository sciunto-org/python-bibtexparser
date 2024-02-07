# python-bibtexparser v2

Welcome to python-bibtexparser, a parser for `.bib` files with a long history and wide adaption.

Bibtexparser is available in two versions: V1 and V2. For new projects, we recommend using v2 which, in the long run, will provide an overall more robust and faster experience. **For now, however, note that v2 is an early beta, and does not contain all features of v1**. Install v2 using pip:

```bash
pip install bibtexparser --pre
```

Or you can install the latest development version directly from the main branch:
```bash
pip install --no-cache-dir --force-reinstall git+https://github.com/sciunto-org/python-bibtexparser@main
```

If instead, you want to use v1, install it using:

```bash
pip install bibtexparser~=1.0
```

Note that all development and maintenance effort is focussed on v2. 
Small PRs for v1 are still accepted, but only as long as they are backwards compatible and don't introduce much additional technical debt.
Development of version one happens on the dedicated [v1 branch](https://github.com/sciunto-org/python-bibtexparser/tree/v1). 

The remainder of this README is specific to v2. 

## Documentation
Go check out our documentation on [https://bibtexparser.readthedocs.io/en/main/](https://bibtexparser.readthedocs.io/en/main/).

## Advantages of V2

- :rocket: Order of magnitudes faster
- :wrench: Easily customizable parsing **and** writing
- :herb: Access to raw, unparsed bibtex.
- :hankey: Fault-Tolerant: Able to parse files with syntax errors
- :mahjong: Massively simplified, robuster handling of de- and encoding (special chars, ...).
- :copyright: Permissive MIT license

## TLDR Usage Example

```python
# Parsing a bibtex string with default values
bib_database = bibtexparser.parse_string(bibtex_string)
# Converting it back to a bibtex string, again with default values
new_bibtex_string = bibtexparser.write_string(bib_database)
```

Slightly more involved example:

```python

# Lets parse some bibtex string.
bib_database = bibtexparser.parse_string(bibtex_string,
    # Middleware layers to transform parsed entries.
    # Here, we split multiple authors from each other and then extract first name, last name, ... for each
    append_middleware=[SeparateCoAuthors(), SplitNameParts()],
)

# Here you have a `bib_database` with all parsed bibtex blocks.

# Let's transform it back to a bibtex_string.
new_bibtex_string = bibtexparser.write_string(bib_database,
    # Revert aboves transfomration
    prepend_middleware=[MergeNameParts(), MergeCoAuthors()]
)
```

These examples really only show the bare minimum. 
Consult the documentation for a list of available middleware, parsing options and write-formatting options.

## V2 Architecture and Terminology

![bibtexparserv2](https://user-images.githubusercontent.com/4815944/193734283-f19f94e8-7986-4acf-b1a3-1d215e297224.png)

The architecture consists of the following components:

#### Library
Reflects the contents of a parsed bibtex files, including all comments, entries, strings, preamples and their metadata (e.g. order). 

#### A Splitter
Splits a bibtex string into basic blocks (Entry, String, Preamble, ...), with correspondingly split content (e.g. fields on Entry, key-value on String, ...).
The splitter aims to be forgiving when facing invalid bibtex: A line starting with a block definition (`@....`) ends the previous block, even if not yet every bracket is closed, failing the parsing of the previous block. Correspondingly, one block type is "ParsingFailedBlock".

#### Middleware
Middleware layers transform a library and its blocks, for example by decoding latex special characters, interpolating string references, resoling crossreferences or re-ordering blocks. Thus, the choice of middleware allows to customize parsing and writing to ones specific usecase. Note: Middlewares, by default, no not mutate their input, but return a modified copy. 

#### Writer
Writes the content of a bibtex library to a `.bib` file. Optional formatting parameters can be passed using a corresponding dedicated data structure.

## About

Since 2022, `bibtexparser` is primarily written and maintained by Michael Weiss ([@MiWeiss](https://github.com/MiWeiss/)). In 2024, Tom de Geus ([@tdegeus](https://github.com/tdegeus)) joined as co-maintainer. 

Credits and thanks to the many contributors who helped creating this library, including
François Boulogne ([@sciunto](https://github.com/sciunto/), creator of the first version) and Olivier Mangin ([@omangin](https://github.com/omangin/), long-term contributor).
