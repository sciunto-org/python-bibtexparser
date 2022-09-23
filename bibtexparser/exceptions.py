from typing import Optional


class ParsingException(Exception):
    """Generic Exception for parsing errors"""

    pass


class BlockAbortedException(ParsingException):
    """Exception where a invalid bibtex file led to an aborted block."""

    def __init__(
        self,
        abort_reason: str,
        # Not provided if end of file is reached
        end_index: Optional[int] = None,
    ):
        self.abort_reason = abort_reason
        self.end_index = end_index


class ParserStateException(ParsingException):
    """Parser is in a self-inflicted invalid state."""

    def __init__(self, message: str):
        self.message = message


class RegexMismatchException(ParserStateException):
    """Raised when regex matches are inconsistent, implying a bug in the parser.

    For example, raised when first match `@string{`
    is not followed by an overlapping match `}`.
    """

    def __init__(self, first_match, expected_match, second_match):
        self.first_match = first_match
        self.expected_match = expected_match
        self.second_match = second_match
        super().__init__(
            f"Regex mismatch: {first_match} followed by {second_match},"
            f"but expected {expected_match}.\n"
            "This is an python-bibtexparser internal error. "
            "Please report this issue at our issue tracker."
        )
