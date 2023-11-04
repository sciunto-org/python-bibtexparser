import logging
import re
from typing import List, Optional, Set, Tuple, Union

from .exceptions import (
    BlockAbortedException,
    ParserStateException,
    RegexMismatchException,
)
from .library import Library
from .model import (
    DuplicateFieldKeyBlock,
    Entry,
    ExplicitComment,
    Field,
    ImplicitComment,
    ParsingFailedBlock,
    Preamble,
    String,
)


class Splitter:
    """Object responsible for splitting a BibTeX string into blocks.

    For each bibtex string, a new Splitter object should be created.
    The splitter is kept as basic as possible in its functionality
    (e.g., enclosing such as `{...}` are not removed).

    This allows for maximum flexibility in the parsing process,
    by subsequently applying middleware."""

    def __init__(self, bibstr: str):
        # Add a newline at the beginning to simplify parsing
        #   (we only allow "@"-block starts after a newline)
        self.bibstr = f"\n{bibstr}"

        self._markiter = None
        self._unaccepted_mark = None

        # Keep track of line we're currently looking at.
        #   `-1` compensates for manually added `\n` above
        self._current_line = -1

        self._reset_block_status(current_char_index=0)

    def _reset_block_status(self, current_char_index):
        self._open_brackets = 0
        self._is_quote_open = False
        self._expected_next: Optional[List[str]] = None

        # By default, we assume that an implicit comment is started
        #   at the beginning of the file and after each @{...} block.
        #   We then ignore empty implicit comments.
        self._implicit_comment_start_line = self._current_line
        self._implicit_comment_start: Optional[int] = current_char_index

    def _end_implicit_comment(self, end_char_index) -> Optional[ImplicitComment]:
        if self._implicit_comment_start is None:
            return  # No implicit comment started

        comment = self.bibstr[self._implicit_comment_start : end_char_index]

        # Clear leading and trailing empty lines,
        #   and count how many lines were removed, to adapt start_line below
        leading_empty_lines = 0
        i = 0
        for i, char in enumerate(comment):
            if char == "\n":
                leading_empty_lines += 1
            elif not char.isspace():
                break

        comment = comment[i:].rstrip()

        if len(comment) > 0:
            return ImplicitComment(
                start_line=self._implicit_comment_start_line + leading_empty_lines,
                raw=comment,
                comment=comment,
            )
        else:
            return None

    def _next_mark(self, accept_eof: bool) -> Optional[re.Match]:
        # Check if there is a mark that was previously not consumed
        #   and return it if so
        if self._unaccepted_mark is not None:
            m = self._unaccepted_mark
            self._unaccepted_mark = None
            self._current_char_index = m.start()
            return m

        # Get next mark from iterator
        m = next(self._markiter, None)
        if m is not None:
            self._current_char_index = m.start()
            if m.group(0) == "\n":
                self._current_line += 1
                return self._next_mark(accept_eof=accept_eof)
        else:
            # Reached end of file
            self._current_char_index = len(self.bibstr)
            if not accept_eof:
                raise BlockAbortedException(
                    abort_reason="Unexpectedly reached end of file.",
                    end_index=self._current_char_index,
                )
        return m

    def _move_to_closed_bracket(self) -> int:
        """Index of the curly bracket closing a just opened one."""
        num_additional_brackets = 0
        while True:
            m = self._next_mark(accept_eof=False)
            if m.group(0) == "{":
                num_additional_brackets += 1
            elif m.group(0) == "}":
                if num_additional_brackets == 0:
                    return m.start()
                else:
                    num_additional_brackets -= 1
            elif m.group(0).startswith("@"):
                self._unaccepted_mark = m
                raise BlockAbortedException(
                    abort_reason=f"Unexpected block start: `{m.group(0)}`. "
                    f"Was still looking for closing bracket",
                    end_index=m.start() - 1,
                )

    def _move_to_comma_or_closing_curly_bracket(
        self, currently_quote_escaped=False, num_open_curls=0
    ) -> int:
        """Index of the end of the field, taking quote-escape into account."""

        if num_open_curls > 0 and currently_quote_escaped:
            raise ParserStateException(
                message="Internal error in parser. "
                "Found a field-value that is both quote-escaped and curly-escaped. "
                "Please report this bug."
            )

        def _is_escaped():
            return currently_quote_escaped or num_open_curls > 0

        # iterate over marks until we find end of field
        while True:
            next_mark = self._next_mark(accept_eof=False)

            # Handle "escape" characters
            if next_mark.group(0) == '"' and not num_open_curls > 0:
                currently_quote_escaped = not currently_quote_escaped
                continue
            elif next_mark.group(0) == "{" and not currently_quote_escaped:
                num_open_curls += 1
                continue
            elif (
                next_mark.group(0) == "}"
                and not currently_quote_escaped
                and num_open_curls > 0
            ):
                num_open_curls -= 1
                continue

            # Check for end of field
            elif next_mark.group(0) == "," and not _is_escaped():
                self._unaccepted_mark = next_mark
                return next_mark.start()
            # Check for end of entry:
            elif next_mark.group(0) == "}" and not _is_escaped():
                self._unaccepted_mark = next_mark
                return next_mark.start()

            # Sanity-check: If new block is starting, we abort
            elif next_mark.group(0).startswith("@"):
                self._unaccepted_mark = next_mark

                if currently_quote_escaped:
                    looking_for = '`"`'
                elif num_open_curls > 0:
                    looking_for = "`}`"
                else:
                    looking_for = "`,` or `}`"

                raise BlockAbortedException(
                    abort_reason=f"Unexpected block start: `{next_mark.group(0)}`. "
                    f"Was still looking for field-value closing {looking_for} ",
                    end_index=next_mark.start() - 1,
                )

    def _move_to_end_of_entry(
        self, first_key_start: int
    ) -> Tuple[List[Field], int, Set[str]]:
        """Move to the end of the entry and return the fields and the end index."""
        result = []
        keys = set()
        duplicate_keys = set()

        key_start = first_key_start
        while True:
            equals_mark = self._next_mark(accept_eof=False)
            if equals_mark.group(0) == "}":
                # End of entry
                return result, equals_mark.end(), duplicate_keys

            if equals_mark.group(0) != "=":
                self._unaccepted_mark = equals_mark
                raise BlockAbortedException(
                    abort_reason="Expected a `=` after entry key, "
                    f"but found `{equals_mark.group(0)}`.",
                    end_index=equals_mark.start(),
                )

            # We follow the convention that the field start line
            #   is where the `=` between key and value is.
            start_line = self._current_line
            key_end = equals_mark.start()
            value_start = equals_mark.end()
            value_end = self._move_to_comma_or_closing_curly_bracket(
                currently_quote_escaped=False, num_open_curls=0
            )

            key = self.bibstr[key_start:key_end].strip()
            value = self.bibstr[value_start:value_end].strip()

            if key in keys:
                duplicate_keys.add(key)

            keys.add(key)
            result.append(Field(start_line=start_line, key=key, value=value))

            # If next mark is a comma, continue
            after_field_mark = self._next_mark(accept_eof=False)
            if after_field_mark.group(0) == ",":
                key_start = after_field_mark.end()
            elif after_field_mark.group(0) == "}":
                # If next mark is a closing bracket, put it back (will return in next loop iteration)
                self._unaccepted_mark = after_field_mark
                continue
            else:
                self._unaccepted_mark = after_field_mark
                raise BlockAbortedException(
                    abort_reason="Expected either a `,` or `}` after a closed entry field value, "
                    f"but found a {after_field_mark.group(0)} before.",
                    end_index=after_field_mark.start(),
                )

    def split(self, library: Optional[Library] = None) -> Library:
        """Split the bibtex-string into blocks and add them to the library.

        Args:
            library: The library to add the blocks to. If None, a new library is created.
        Returns:
            The library with the added blocks.
        """
        self._markiter = re.finditer(
            r"(?<!\\)[\{\}\",=\n]|@[\w]*( |\t)*(?={)", self.bibstr, re.MULTILINE
        )

        if library is None:
            library = Library()
        else:
            logging.info("Adding blocks to existing library.")

        while True:
            m = self._next_mark(accept_eof=True)
            if m is None:
                break

            m_val = m.group(0).lower()

            if m_val.startswith("@"):
                # Clean up previous block implicit_comment
                implicit_comment = self._end_implicit_comment(m.start())
                if implicit_comment is not None:
                    library.add(implicit_comment)
                self._implicit_comment_start = None

                start_line = self._current_line
                try:
                    # Start new block parsing
                    if m_val.startswith("@comment"):
                        library.add(self._handle_explicit_comment())
                    elif m_val.startswith("@preamble"):
                        library.add(self._handle_preamble())
                    elif m_val.startswith("@string"):
                        library.add(self._handle_string(m))
                    else:
                        library.add(self._handle_entry(m, m_val))

                except BlockAbortedException as e:
                    logging.warning(
                        f"Parsing of `{m_val}` block (line {start_line}) aborted on line {self._current_line}  "
                        f"due to syntactical error in bibtex:\n {e.abort_reason}"
                    )
                    logging.info(
                        "We will try to continue parsing, but this might lead to unexpected results."
                        "The failed block will be stored in the `failed_blocks`of the library."
                    )
                    library.add(
                        ParsingFailedBlock(
                            start_line=start_line,
                            raw=self.bibstr[m.start() : e.end_index],
                            error=e,
                        )
                    )

                except ParserStateException as e:
                    # This is a bug in the parser, not in the bibtex. We should not continue.
                    logging.error(
                        "python-bibtexparser detected an invalid state. "
                        "Please report this bug."
                    )
                    logging.error(e.message)
                    raise e
                except Exception as e:
                    # For unknown exeptions, we want to fail hard and get the info in our issue tracker.
                    logging.error(
                        f"Unexpected exception while parsing `{m_val}` block (line {start_line})"
                        "Please report this bug."
                    )
                    raise e

                self._reset_block_status(
                    current_char_index=self._current_char_index + 1
                )
            else:
                # Part of implicit comment
                continue

        # Check if there's an implicit comment at the EOF
        if self._implicit_comment_start is not None:
            comment = self._end_implicit_comment(len(self.bibstr))
            if comment is not None:
                library.add(comment)

        return library

    def _handle_explicit_comment(self) -> ExplicitComment:
        """Handle explicit comment block. Return end index"""
        start_index = self._current_char_index
        start_line = self._current_line
        start_bracket_mark = self._next_mark(accept_eof=False)
        if start_bracket_mark.group(0) != "{":
            self._unaccepted_mark = start_bracket_mark
            # Note: The following should never happen, as we check for the "{" in the regex
            raise RegexMismatchException(
                first_match="@comment{",
                expected_match="{",
                second_match=start_bracket_mark.group(0),
            )
        end_bracket_index = self._move_to_closed_bracket()
        comment_str = self.bibstr[start_bracket_mark.end() : end_bracket_index].strip()
        return ExplicitComment(
            start_line=start_line,
            comment=comment_str,
            raw=self.bibstr[start_index : end_bracket_index + 1],
        )

    def _handle_entry(self, m, m_val) -> Union[Entry, ParsingFailedBlock]:
        """Handle entry block. Return end index"""
        start_line = self._current_line
        entry_type = m_val[1:].strip()
        start_bracket_mark = self._next_mark(accept_eof=False)
        if start_bracket_mark.group(0) != "{":
            self._unaccepted_mark = start_bracket_mark
            # Note: The following should never happen, as we check for the "{" in the regex
            raise ParserStateException(
                message="matched a regex that should end with `{`, "
                "e.g. `@article{`, "
                "but no closing bracket was found."
            )
        comma_mark = self._next_mark(accept_eof=False)
        if comma_mark.group(0) == "}":
            # This is an entry without any comma after the key, and with no fields
            #   Used e.g. by RefTeX (see issue #384)
            key = self.bibstr[m.end() + 1 : comma_mark.start()].strip()
            fields, end_index, duplicate_keys = [], comma_mark.end(), []
        elif comma_mark.group(0) != ",":
            self._unaccepted_mark = comma_mark
            raise BlockAbortedException(
                abort_reason="Expected comma after entry key,"
                f" but found {comma_mark.group(0)}",
                end_index=comma_mark.end(),
            )
        else:
            self._open_brackets += 1
            key = self.bibstr[m.end() + 1 : comma_mark.start()].strip()
            fields, end_index, duplicate_keys = self._move_to_end_of_entry(
                comma_mark.end()
            )

        entry = Entry(
            start_line=start_line,
            entry_type=entry_type,
            key=key,
            fields=fields,
            raw=self.bibstr[m.start() : end_index],
        )

        # If there were duplicate field keys, we return a DuplicateFieldKeyBlock wrapping
        if len(duplicate_keys) > 0:
            return DuplicateFieldKeyBlock(duplicate_keys=duplicate_keys, entry=entry)
        else:
            return entry

    def _handle_string(self, m) -> String:
        """Handle string block. Return end index"""
        # Get next mark, which should be an equals sign
        start_i = self._current_char_index
        start_line = self._current_line
        start_bracket_mark = self._next_mark(accept_eof=False)
        if start_bracket_mark.group(0) != "{":
            self._unaccepted_mark = start_bracket_mark
            # Note: The following should never happen, as we check for the "{" in the regex
            raise ParserStateException(
                message="matched a string def regex (`@string{`) that "
                "should end with `{`, but no closing bracket was found."
            )
        equals_mark = self._next_mark(accept_eof=False)
        if equals_mark.group(0) != "=":
            self._unaccepted_mark = equals_mark
            raise BlockAbortedException(
                abort_reason="Expected equals sign after field key,"
                f" but found {equals_mark.group(0)}",
                end_index=equals_mark.end(),
            )
        key = self.bibstr[m.end() + 1 : equals_mark.start()].strip()
        value_start = equals_mark.end()
        end_i = self._move_to_closed_bracket()
        value = self.bibstr[value_start:end_i].strip()
        return String(
            start_line=start_line,
            key=key,
            value=value,
            raw=self.bibstr[start_i : end_i + 1],
        )

    def _handle_preamble(self) -> Preamble:
        """Handle preamble block. Return end index"""
        start_i = self._current_char_index
        start_line = self._current_line
        start_bracket_mark = self._next_mark(accept_eof=False)
        if start_bracket_mark.group(0) != "{":
            self._unaccepted_mark = start_bracket_mark
            # Note: The following should never happen, as we check for the "{" in the regex
            raise ParserStateException(
                message="matched a preamble def regex (`@preamble{`) that "
                "should end with `{`, but no closing bracket was found."
            )

        end_bracket_index = self._move_to_closed_bracket()
        preamble = self.bibstr[start_bracket_mark.end() : end_bracket_index]
        return Preamble(
            start_line=start_line,
            value=preamble,
            raw=self.bibstr[start_i : end_bracket_index + 1],
        )
