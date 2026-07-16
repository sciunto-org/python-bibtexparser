================
Biber & BibLaTeX
================

BibLaTeX normally uses Biber to process BibTeX-format data sources. It extends
the traditional BibTeX data model with additional entry types, fields, lists,
dates, inheritance mechanisms, annotations, and name forms. Biber also permits
custom data models. The structural parser therefore accepts entry-type and field
names without restricting them to either project's built-in schema.

The test suite covers representative BibLaTeX and Biber constructs separately
from traditional BibTeX examples, including:

* ``@set`` and ``@xdata`` entries;
* extended name forms and data annotations;
* date ranges, UTF-8 values, and BibLaTeX-specific entry types and fields;
* names supplied by a custom Biber data model.

These constructs use the normal parser and writer defaults. No dialect option is
needed merely to retain them. Their subgrammars remain uninterpreted strings
unless a caller explicitly applies suitable middleware. In particular, the
parser does not validate a BibLaTeX data model, resolve entry sets or inheritance,
or interpret names, lists, annotations, and dates as typed values. Use Biber when
those semantics or validation are required.

This is not a claim that every concrete syntax accepted by Biber is implemented.
In particular, parenthesis-delimited blocks are outside the currently tested
structural-compatibility profile. Curly-brace-delimited data sources provide the
profile covered here.

Converting between the traditional BibTeX and BibLaTeX data models is also not a
default parsing operation. BibLaTeX contains information with no general
lossless BibTeX equivalent, so a future converter must use an explicit mapping
profile and report every lossy or ambiguous decision. Such conversion belongs in
opt-in transformation middleware or a higher-level bibliography tool rather than
in the structural codec defaults.
