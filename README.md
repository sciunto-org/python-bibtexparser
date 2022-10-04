# python-bibtexparser v2

This is the (very early) development version of python-bibtexparser v2. 
It is not yet ready for production use, and major breaking changes and refactoring are still to come.

The files in here are also still buggy, so don't copy-paste snippets either :-)

If you want to join the development, please contact us through github issues. 

## v2-architecture

![bibtexparserv2](https://user-images.githubusercontent.com/4815944/193734283-f19f94e8-7986-4acf-b1a3-1d215e297224.png)

The architecture consists of the following components:

#### A Splitter
Splits a bibtex string into basic blocks (Entry, String, Preamble, ...), with correspondingly split content (e.g. fields on Entry, key-value on String, ...).

The splitter differs from the `v1` parser in that it is more forgiving when facing invalid bibtex: A line starting with a block definition (`@....`) ends the previous block, even if not yet every bracket is closed. Correspondingly, on block type is "ParsingFailedBlock".

As opposed to `v1`, which relies on pyparsing, the `v2` splitter is much more narrow in its scope, custom written and orders of magnitude faster.

#### Middleware
TODO Describe

#### Writer
TODO Describe

#### Library
TODO Describe
