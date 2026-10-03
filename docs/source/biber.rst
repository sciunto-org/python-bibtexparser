================
Biber & Biblatex
================


Due to its simple and high-level nature, this library should not only support BibTeX, but also be able to parse biblatex and biber files
with ease, as they all share the same general syntax.

That said, we did not explicitly check against all of biber and biblatex features. Should you detect anything which is not supported,
please open an issue or send a pull request.

Comments within entries
=======================

Biber allows ``%``-comments within entries, e.g. to comment out a field:

.. code-block:: bibtex

    @article{Cesar2013,
      author = {Jean César},
      % title = {An amazing title},
    }

Where a field key is expected, bibtexparser reads ``%`` up to the end of the line as such a comment.
Comments before a field are available as ``field.comments``,
comments after the last field as ``entry.trailing_comments``.
When writing, they are written on the lines above their field, or above the closing brace of the entry.

A comment extends to the end of the line, as in biber,
hence a closing brace of the entry on the same line is commented out as well.
Within field values and entry keys, ``%`` is a literal character, as in BibTeX.
Note that a comment is only recognized after the comma ending the previous field:
in ``year = 2020 % comment``, without a comma before the ``%``, the comment becomes part of the value.
