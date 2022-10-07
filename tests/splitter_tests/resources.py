import pytest

FIELD_VALUE_EDGE_CASES = [
    "John Doe",
    r'à {\`a} \`{a}',
    r'{\`a} {\`a} {\`a}',
    r"Two Gedenk\"uberlieferung der Angelsachsen",
    r"\texttimes{}{\texttimes}\texttimes",
    r"p\^{a}t\'{e}"
    r"Title with \{ a curly brace",
    r"Title with \} a curly brace",
    r"Title with \{ a curly brace and \} a curly brace",
    r"Title with \{ a curly brace and \} a curly brace and \{ another curly brace",
    r"Title with { UnEscaped Curly } Braces",
]

FIELD_VALUE_EDGE_CASES_ENCLOSINGS = [
    pytest.param('"{0}"', id="double_quotes"),
    pytest.param("{{{0}}}", id="curly_braces"),
]
