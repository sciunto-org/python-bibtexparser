from typing import List, Optional


class ParsingException(Exception):
    """Generic Exception for parsing errors"""

    def __copy__(self):
        # We do not copy or deepcopy ParsingExceptions
        # because they are used as immutables,
        # and because default memo fails.
        return self

    def __deepcopy__(self, memo):
        # We do not copy or deepcopy ParsingExceptions
        # because they are used as immutables,
        # and because default memo fails.
        return self


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

    For example, raised when first match ``@string{``
    is not followed by an overlapping match ``}``.
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


class PartialMiddlewareException(ParsingException):
    """Exception raised when a middleware could not be fully applied."""

    def __init__(self, reasons: List[str]):
        reasons_string = "\n\n=====\n\n".join(reasons)
        super().__init__(f"Middleware could not be fully applied: {reasons_string}")
