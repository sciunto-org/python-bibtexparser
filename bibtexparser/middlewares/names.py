"""Middlewares regarding person names.

Much of the code is taken from Blair Bonnetts never merged v0 pull request
(https://github.com/sciunto-org/python-bibtexparser/pull/140).
"""
import abc
import dataclasses
from typing import List, Literal, Tuple

from bibtexparser.model import Block, Entry, Field, MiddlewareErrorBlock

from .middleware import BlockMiddleware


class InvalidNameError(ValueError):
    """Exception raised by :py:func:`parse_single_name_into_parts` when facing an invalid name."""

    def __init__(self, name: str, reason: str):
        message: str = f"Cannot split the following name `{name}` into parts: {reason}"
        super().__init__(message)


class _NameTransformerMiddleware(BlockMiddleware, abc.ABC):
    """Internal utility class - superclass for all name-transforming middlewares.

    :param allow_inplace_modification: See corresponding property.
    :param name_fields: The fields that contain names, considered by this middleware."""

    def __init__(
        self,
        allow_inplace_modification: bool = True,
        name_fields: Tuple[str] = ("author", "editor", "translator"),
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )
        self._name_fields = name_fields

    @property
    def name_fields(self) -> Tuple[str]:
        """The fields that contain names, considered by this middleware."""
        return self._name_fields

    @abc.abstractmethod
    def _transform_field_value(self, name):
        raise NotImplementedError("called abstract method")

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        field: Field
        try:
            for field in entry.fields:
                if field.key in self.name_fields:
                    field.value = self._transform_field_value(field.value)
            return entry
        except InvalidNameError as e:
            return MiddlewareErrorBlock(entry, e)


class SeparateCoAuthors(_NameTransformerMiddleware):
    """Middleware to separate multi-person fields (e.g. co-authors, co-editors)."""

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "separate_coauthors"

    # docstr-coverage: inherited
    def _transform_field_value(self, name) -> List[str]:
        return split_multiple_persons_names(name)


class MergeCoAuthors(_NameTransformerMiddleware):
    """Middleware to merge multi-person-list fields (e.g. co-authors, co-editors)."""

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "merge_coauthors"

    # docstr-coverage: inherited
    def _transform_field_value(self, name):
        if isinstance(name, list):
            return " and ".join(name)
        return name


@dataclasses.dataclass
class NameParts:
    """A dataclass representing the parts of a person name.

    The different parts are defined according to BibTex's implementation
    of name parts (first, von, last, jr)."""

    first: List[str] = dataclasses.field(default_factory=list)
    von: List[str] = dataclasses.field(default_factory=list)
    last: List[str] = dataclasses.field(default_factory=list)
    jr: List[str] = dataclasses.field(default_factory=list)

    @property
    def merge_first_name_first(self) -> str:
        """Merging the name parts into a single string, first-name-first (no comma) format."""
        return " ".join(
            [
                part
                for part in (
                    " ".join(self.first) if self.first else None,
                    " ".join(self.von) if self.von else None,
                    " ".join(self.last) if self.last else None,
                    " ".join(self.jr) if self.jr else None,
                )
                if part is not None
            ]
        )

    @property
    def merge_last_name_first(self) -> str:
        """Merging the name parts into a single string, last-name-first (with commas) format.

        The structure of the output is: `von Last, Jr, First`
        """

        def escape_last_slash(string: str) -> str:
            """Escape the last slash in a string if it is not escaped."""
            # Find the number of trailing slashes
            stripped = string.rstrip("\\")
            num_slashes = len(string) - len(stripped)
            if num_slashes % 2 == 0:
                # Even number: everything is escaped
                return string
            else:
                # Odd number: need to escape one.
                return string + "\\"

        first = " ".join(self.first) if self.first else None
        von = " ".join(self.von) if self.von else None
        last = " ".join(self.last) if self.last else None
        jr = " ".join(self.jr) if self.jr else None

        von_last = " ".join(name for name in [von, last] if name)
        return ", ".join(
            escape_last_slash(name) for name in [von_last, jr, first] if name
        )


class SplitNameParts(_NameTransformerMiddleware):
    """Middleware to split a persons name into its parts (first, von, last, jr).

    Name fields (e.g. author, editor, translator) are expected to be lists of strings,
    which can be achieved by using the `SeparateCoAuthors` middleware before this one.
    """

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "split_name_parts"

    def _transform_field_value(self, name) -> List[NameParts]:
        if not isinstance(name, list):
            raise ValueError(
                "Expected a list of strings, got {}. "
                "Make sure to use `SeparateCoAuthors` middleware"
                "before using `SplitNameParts` middleware".format(name)
            )

        return [parse_single_name_into_parts(n) for n in name]


class MergeNameParts(_NameTransformerMiddleware):
    """Middleware to merge a persons name parts (first, von, last, jr) into a single string.

    Name fields (e.g. author, editor, translator) are expected to be lists of NameParts.

    The merging style indicates whether:
    - the merging is done without commas in first-name-first order ("first"), or
    - the merging is done with commas in last-name-first order ("last").
    """

    def __init__(
        self,
        style: Literal["last", "first"] = "last",
        allow_inplace_modification: bool = True,
        name_fields: Tuple[str] = ("author", "editor", "translator"),
    ):
        self.style = style
        super().__init__(allow_inplace_modification, name_fields)

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "merge_name_parts"

    def _transform_field_value(self, name) -> List[str]:
        if not isinstance(name, list) and all(isinstance(n, NameParts) for n in name):
            raise ValueError("Expected a list of NameParts, got {}. ".format(name))

        if self.style == "last":
            return [n.merge_last_name_first for n in name]
        elif self.style == "first":
            return [n.merge_first_name_first for n in name]
        else:
            raise ValueError(
                """Expected "first" or "last" style, got {}. """.format(self.style)
            )


def parse_single_name_into_parts(name, strict=True):
    """
    Parse a name into its constituent parts: First, von, Last, and Jr.

    :param string name: a string containing a single name
    :param Boolean strict: whether to use strict mode
    :returns: dictionary of constituent parts
    :raises `utils.InvalidName`: If an invalid name is given and
                                 ``strict_mode = True``.

    In BibTeX, a name can be represented in any of three forms:
        * First von Last
        * von Last, First
        * von Last, Jr, First

    This function attempts to break a given name into its four parts. The
    returned dictionary has keys of ``first``, ``last``, ``von`` and ``jr``.
    Each value is a list of the words making up that part; this may be an empty
    list.  If the input has no non-whitespace characters, a blank dictionary is
    returned.

    It is capable of detecting some errors with the input name. If the
    ``strict_mode`` parameter is ``True``, which is the default, this results in
    a :class:`utils.InvalidName` exception being raised. If it is ``False``,
    the function continues, working around the error as best it can.  The
    errors that can be detected are listed below along with the handling
    for non-strict mode:

        * Name finishes with a trailing comma: delete the comma
        * Too many parts (e.g., von Last, Jr, First, Error): merge extra parts
          into First
        * Unterminated opening brace: add closing brace to end of input
        * Unmatched closing brace: add opening brace at start of word

    Examples::

        >>> parse_single_name_into_parts("Donald E. Knuth")
        {'last': ['Knuth'], 'von': [], 'first': ['Donald', 'E.'], 'jr': []}

        >>> parse_single_name_into_parts("Brinch Hansen, Per")
        {'last': ['Brinch', 'Hansen'], 'von': [], 'first': ['Per'], 'jr': []}

        >>> parse_single_name_into_parts("Beeblebrox, IV, Zaphod")
        {'last': ['Beeblebrox'], 'von': [], 'first': ['Zaphod'], 'jr': ['IV']}

        >>> parse_single_name_into_parts("Ludwig van Beethoven")
        {'last': ['Beethoven'], 'von': ['van'], 'first': ['Ludwig'], 'jr': []}

    """
    # Useful references:
    # http://maverick.inria.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html#names
    # http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf

    # Whitespace characters that can separate words.
    whitespace = set(" ~\r\n\t")

    # We'll iterate over the input once, dividing it into a list of words for
    # each comma-separated section. We'll also calculate the case of each word
    # as we work.
    sections = [[]]  # Sections of the name.
    cases = [[]]  # 1 = uppercase, 0 = lowercase, -1 = caseless.
    word = []  # Current word.
    case = -1  # Case of the current word.
    level = 0  # Current brace level.
    bracestart = False  # Will the next character be the first within a brace?
    controlseq = True  # Are we currently processing a control sequence?
    specialchar = None  # Are we currently processing a special character?

    # Using an iterator allows us to deal with escapes in a simple manner.
    nameiter = iter(name)
    for char in nameiter:
        # An escape.
        if char == "\\":
            try:
                escaped = next(nameiter)

                # BibTeX doesn't allow whitespace escaping. Copy the slash and fall
                # through to the normal case to handle the whitespace.
                if escaped in whitespace:
                    word.append(char)
                    char = escaped

                else:
                    # Is this the first character in a brace?
                    if bracestart:
                        bracestart = False
                        controlseq = escaped.isalpha()
                        specialchar = True

                    # Can we use it to determine the case?
                    elif (case == -1) and escaped.isalpha():
                        if escaped.isupper():
                            case = 1
                        else:
                            case = 0

                    # Copy the escape to the current word and go to the next
                    # character in the input.
                    word.append(char)
                    word.append(escaped)
                    continue

            # If we're at the end of the string, then the \ is just a \.
            except StopIteration:
                word.append(char)

        # Start of a braced expression.
        if char == "{":
            level += 1
            word.append(char)
            bracestart = True
            controlseq = False
            specialchar = False
            continue

        # All the below cases imply this (and don't test its previous value).
        bracestart = False

        # End of a braced expression.
        if char == "}":
            # Check and reduce the level.
            if level:
                level -= 1
            else:
                if strict:
                    raise InvalidNameError(name=name, reason="Unmatched closing brace")
                word.insert(0, "{")

            # Update the state, append the character, and move on.
            controlseq = False
            specialchar = False
            word.append(char)
            continue

        # Inside a braced expression.
        if level:
            # Is this the end of a control sequence?
            if controlseq:
                if not char.isalpha():
                    controlseq = False

            # If it's a special character, can we use it for a case?
            elif specialchar:
                if (case == -1) and char.isalpha():
                    if char.isupper():
                        case = 1
                    else:
                        case = 0

            # Append the character and move on.
            word.append(char)
            continue

        # End of a word.
        # NB. we know we're not in a brace here due to the previous case.
        if char == "," or char in whitespace:
            # Don't add empty words due to repeated whitespace.
            if word:
                sections[-1].append("".join(word))
                word = []
                cases[-1].append(case)
                case = -1
                controlseq = False
                specialchar = False

            # End of a section.
            if char == ",":
                if len(sections) < 3:
                    sections.append([])
                    cases.append([])
                elif strict:
                    raise InvalidNameError(name=name, reason="Too many commas")
            continue

        # Regular character.
        word.append(char)
        if (case == -1) and char.isalpha():
            if char.isupper():
                case = 1
            else:
                case = 0

    # Unterminated brace?
    if level:
        if strict:
            raise InvalidNameError(name=name, reason="Unterminated opening brace")
        while level:
            word.append("}")
            level -= 1

    # Handle the final word.
    if word:
        sections[-1].append("".join(word))
        cases[-1].append(case)

    # Get rid of trailing sections.
    if not sections[-1]:
        # Trailing comma?
        if (len(sections) > 1) and strict:
            raise InvalidNameError(name=name, reason="Trailing comma at end of name")
        sections.pop(-1)
        cases.pop(-1)

    # No non-whitespace input.
    if not sections or not any(bool(section) for section in sections):
        return NameParts()

    # Initialise the output dictionary.
    parts = NameParts()

    # Form 1: "First von Last"
    if len(sections) == 1:
        p0 = sections[0]

        # One word only: last cannot be empty.
        if len(p0) == 1:
            parts.last = p0

        # Two words: must be first and last.
        elif len(p0) == 2:
            parts.first = p0[:1]
            parts.last = p0[1:]

        # Need to use the cases to figure it out.
        else:
            cases = cases[0]

            # First is the longest sequence of words starting with uppercase
            # that is not the whole string. von is then the longest sequence
            # whose last word starts with lowercase that is not the whole
            # string. Last is the rest. NB., this means last cannot be empty.

            # At least one lowercase letter.
            if 0 in cases:
                # Index from end of list of first and last lowercase word.
                firstl = cases.index(0) - len(cases)
                lastl = -cases[::-1].index(0) - 1
                if lastl == -1:
                    lastl -= 1  # Cannot consume the rest of the string.

                # Pull the parts out.
                parts.first = p0[:firstl]
                parts.von = p0[firstl : lastl + 1]
                parts.last = p0[lastl + 1 :]

            # No lowercase: last is the last word, first is everything else.
            else:
                parts.first = p0[:-1]
                parts.last = p0[-1:]

    # Form 2 ("von Last, First") or 3 ("von Last, jr, First")
    else:
        # As long as there is content in the first name partition, use it as-is.
        first = sections[-1]
        if first and first[0]:
            parts.first = first

        # And again with the jr part.
        if len(sections) == 3:
            jr = sections[-2]
            if jr and jr[0]:
                parts.jr = jr

        # Last name cannot be empty; if there is only one word in the first
        # partition, we have to use it for the last name.
        last = sections[0]
        if len(last) == 1:
            parts.last = last

        # Have to look at the cases to figure it out.
        else:
            lcases = cases[0]

            def rindex(l, x, default):
                """Returns the index of the rightmost occurence of x in l."""
                for i in range(len(l) - 1, -1, -1):
                    if l[i] == x:
                        return i
                return default

            # Check if at least one of the words is lowercase
            if 0 in lcases:
                # Excluding the last word, find the index of the last lower word
                split = rindex(lcases[:-1], 0, -1) + 1
                parts.von = sections[0][:split]
                parts.last = sections[0][split:]

            # All uppercase => all last.
            else:
                parts.last = sections[0]

    # Done.
    return parts


def split_multiple_persons_names(names):
    """
    Splits a string of multiple names.

    :param string names: a string containing one or more names
    :returns: list of strings, one entry per name in the input

    In BibTeX a set of names (e.g., authors or editors) are separated by the
    word 'and'. Any instances of the word 'and' within a pair of braces is
    treated as part of the name, and not a separator.

    This function takes a string containing one or more names, and splits them
    into a list of individual names. They are returned as a list of strings. If
    the input contains only whitespace characters, an empty list is returned.

    Note that for consistency with the way BibTeX splits strings, the
    non-breaking space or tie '~' is treated as a regular character and not
    whitespace.

    No error checking is performed on the individual names, i.e., there is no
    guarantee that the entries in the returned list are valid BibTeX names.

    Examples::

        >>> split_multiple_persons_names('Donald E. Knuth')
        ['Donald E. Knuth']

        >>> split_multiple_persons_names('Donald E. Knuth and Leslie Lamport')
        ['Donald E. Knuth', 'Leslie Lamport']

        >>> split_multiple_persons_names('{Simon and Schuster}')
        ['{Simon and Schuster}']

    """
    # Sanity check for empty string.
    names = names.strip(" \r\n\t")
    if not names:
        return []

    # Steps to find the ' and ' token.
    START_WHITESPACE, FIND_A, FIND_N, FIND_D, END_WHITESPACE, NEXT_WORD = (
        0,
        1,
        2,
        3,
        4,
        5,
    )

    # Processing variables.
    step = START_WHITESPACE  # Current step.
    pos = 0  # Current position in string.
    bracelevel = 0  # Current bracelevel.
    spans = [[0]]  # Spans of names within the string.
    possible_end = 0  # Possible end position of a name.
    whitespace = set(" \r\n\t")  # Allowed whitespace characters.

    # Loop over the string.
    namesiter = iter(names)
    for char in namesiter:
        pos += 1

        # Escaped character.
        if char == "\\":
            try:
                next(namesiter)
            # If we're at the end of the string, then the \ is just a \.
            except StopIteration:
                pass
            pos += 1
            continue

        # Change in brace level.
        if char == "{":
            if step == NEXT_WORD:
                spans[-1].append(possible_end)
                spans.append([pos - 1])
            bracelevel += 1
            step = START_WHITESPACE
            continue
        if char == "}":
            if bracelevel:
                bracelevel -= 1
            step = START_WHITESPACE
            continue

        # Ignore everything inside a brace.
        if bracelevel:
            step = START_WHITESPACE
            continue

        # Looking for a whitespace character to start the ' and '. When we find
        # one, mark it as the possible end of the previous word.
        if step == START_WHITESPACE:
            if char in whitespace:
                step = FIND_A
                possible_end = pos - 1

        # Looking for the letter a. NB., we can have multiple whitespace
        # characters so we need to handle that here.
        elif step == FIND_A:
            if char in ("a", "A"):
                step = FIND_N
            elif char not in whitespace:
                step = START_WHITESPACE

        # Looking for the letter n.
        elif step == FIND_N:
            if char in ("n", "N"):
                step = FIND_D
            else:
                step = START_WHITESPACE

        # Looking for the letter d.
        elif step == FIND_D:
            if char in ("d", "D"):
                step = END_WHITESPACE
            else:
                step = START_WHITESPACE

        # And now the whitespace to end the ' and '.
        elif step == END_WHITESPACE:
            if char in whitespace:
                step = NEXT_WORD
            else:
                step = START_WHITESPACE

        # Again, we need to handle multiple whitespace characters. Keep going
        # until we find the start of the next word.
        elif step == NEXT_WORD:
            if char not in whitespace:
                # Finish the previous word span, start the next,
                # and do it all again.
                spans[-1].append(possible_end)
                spans.append([pos - 1])
                step = START_WHITESPACE

    # Finish the last word.
    spans[-1].append(None)

    # Extract and return the names.
    return [names[start:end] for start, end in spans]
