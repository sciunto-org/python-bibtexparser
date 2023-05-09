# python-bibtexparser v2

This is the development branch of python-bibtexparser v2.
It is not yet ready for production use, and some breaking changes and refactoring may still to come.

However, the majority of functionality is implemented and as bibtexparser v1 will soon stop getting updates, 
it might be worth to check out this branch and give it a try.

```bash
pip install git+https://github.com/sciunto-org/python-bibtexparser@v2
```

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


