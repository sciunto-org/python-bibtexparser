from textwrap import dedent

import pytest

EDGE_CASE_VALUES: list[str] = [
    "John Doe",
    r"à {\`a} \`{a}",
    r"{\`a} {\`a} {\`a}",
    r"Two Gedenk\"uberlieferung der Angelsachsen",
    r"\texttimes{}{\texttimes}\texttimes",
    r"p\^{a}t\'{e}" r"Title with \{ a curly brace",
    r"Title with \} a curly brace",
    r"Title with \{ a curly brace and \} a curly brace",
    r"Title with \{ a curly brace and \} a curly brace and \{ another curly brace",
    r"Title with { UnEscaped Curly } Braces",
]

ENCLOSINGS: list[pytest.param] = [
    pytest.param('"{0}"', id="double_quotes"),
    pytest.param("{{{0}}}", id="curly_braces"),
]

VALID_BIBTEX_SNIPPETS: list[str] = [
    # A small, regular article
    dedent("""\
    @article{test,
        author = "John Doe",
        title = "Some title",
    }"""),
    # A string definition
    dedent("""@string{someString = "some value"}"""),
    # A string definition with a comment
    dedent("""\
    @string{someString = "some value"}

    % This is a comment"""),
    # A preamble
    dedent("""@preamble{some preamble}"""),
    # A an empty line
    "\n",
    # A comment
    "% This is a comment",
]

PREAMBLES = [
    "ax + b",
    "ax + b + c",
    "a^2 + 2ab + b^2",
    r"\{a_1, a_2, a_3\}",
]
