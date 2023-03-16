import abc
from collections import OrderedDict
from typing import Union, Tuple

from bibtexparser.library import Library
from bibtexparser.middlewares.middleware import BlockMiddleware
from bibtexparser.model import (
    Block,
    Entry, Field,
)


class _MonthInterpolator(BlockMiddleware, abc.ABC):
    """Abstract class to handle month-conversions."""

    # docstr-coverage: inherited
    def __init__(self, allow_inplace_modification: bool):
        super().__init__(allow_inplace_modification, allow_parallel_execution=True)

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: "Library") -> Block:
        try:
            month = entry.fields["month"]
        except KeyError:
            return entry

        new_val, meta = self.resolve_month_field_val(month)
        month.value = new_val
        entry.parser_metadata[self.metadata_key()] = meta
        return entry

    @abc.abstractmethod
    def resolve_month_field_val(self, month_field: Field) -> Tuple[Union[str, int], str]:
        """Transform the month field.

        Args:
            month_field: The month field to transform.

        Returns:
            A tuple of the transformed value and the metadata."""
        raise NotImplementedError("Abstract method")


_MONTH_ABBREV_TO_FULL = OrderedDict([
    ('jan', 'January'),
    ('feb', 'February'),
    ('mar', 'March'),
    ('apr', 'April'),
    ('may', 'May'),
    ('jun', 'June'),
    ('jul', 'July'),
    ('aug', 'August'),
    ('sep', 'September'),
    ('oct', 'October'),
    ('nov', 'November'),
    ('dec', 'December')
])

_MONTH_ABBREV = list(_MONTH_ABBREV_TO_FULL.keys())

_MONTH_FULL = list(_MONTH_ABBREV_TO_FULL.values())

_LOWERCASE_FULL_SET = set(m.lower() for m in _MONTH_FULL)


class MonthLongStringMiddleware(_MonthInterpolator):
    """Replace month numbers with full month names."""

    @staticmethod
    def metadata_key() -> str:
        return "MonthLongStringMiddleware"

    # docstr-coverage: inherited
    def resolve_month_field_val(self, month_field: Field):
        v = month_field.value
        if isinstance(v, int):
            if v < 1 or v > 12:
                return month_field  # Nothing we can do here
            month_field.value = _MONTH_ABBREV_TO_FULL[v], "transformed int-month to str-month"
        elif isinstance(v, str):
            v_lower = v.lower()

            if v_lower in _MONTH_ABBREV_TO_FULL:
                month_field.value = _MONTH_ABBREV_TO_FULL[v_lower], "transformed abbreviated month to full month"
            elif v_lower in _LOWERCASE_FULL_SET:
                default_casing = _MONTH_ABBREV_TO_FULL[v_lower[:3]]
                if v != default_casing:
                    month_field.value = default_casing, "transformed month casing"

        # We can't do anything else here
        return month_field, "month field unchanged"


class MonthAbbreviationMiddleware(_MonthInterpolator):
    """Replace month values with month abbreviations"""

    @staticmethod
    def metadata_key() -> str:
        return "MonthAbbreviationMiddleware"

    # docstr-coverage: inherited
    def resolve_month_field_val(self, month_field: Field):
        v = month_field.value
        if isinstance(v, int):
            if v < 1 or v > 12:
                return month_field
            month_field.value = _MONTH_ABBREV[v], "transformed int-month to abbreviated month"
        elif isinstance(v, str):
            v_lower = v.lower()
            if v_lower in _LOWERCASE_FULL_SET:
                month_field.value = v_lower[:3], "transformed full month to abbreviated month"
            elif v_lower in _MONTH_ABBREV and not v_lower == v:
                month_field.value = v_lower, "use lowercase month abbreviation"

        return month_field, "month field unchanged"


class MonthIntMiddleware(_MonthInterpolator):
    """Replace month values with month numbers"""

    @staticmethod
    def metadata_key() -> str:
        return "MonthIntMiddleware"

    # docstr-coverage: inherited
    def resolve_month_field_val(self, month_field: Field):
        v = month_field.value
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in _LOWERCASE_FULL_SET:
                month_field.value = _MONTH_FULL.index(v_lower[:3]) + 1, "transformed full month to int-month"
            elif v_lower in _MONTH_ABBREV:
                month_field.value = _MONTH_ABBREV.index(v_lower) + 1, "transformed abbreviated month to int-month"

        return month_field, "month field unchanged"
