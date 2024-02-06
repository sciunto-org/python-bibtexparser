import abc
from collections import OrderedDict
from typing import Tuple, Union

from bibtexparser.library import Library
from bibtexparser.model import Block, Entry, Field

from .middleware import BlockMiddleware


class _MonthInterpolator(BlockMiddleware, abc.ABC):
    """Abstract class to handle month-conversions."""

    # docstr-coverage: inherited
    def __init__(self, allow_inplace_modification: bool = True):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: "Library") -> Block:
        try:
            month = entry.fields_dict["month"]
        except KeyError:
            return entry

        new_val, meta = self.resolve_month_field_val(month)
        month.value = new_val
        entry.parser_metadata[self.metadata_key()] = meta
        return entry

    @abc.abstractmethod
    def resolve_month_field_val(
        self, month_field: Field
    ) -> Tuple[Union[str, int], str]:
        """Transform the month field.

        Args:
            month_field: The month field to transform.

        Returns:
            A tuple of the transformed value and the metadata."""
        raise NotImplementedError("Abstract method")


_MONTH_ABBREV_TO_FULL = OrderedDict(
    [
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)

_MONTH_ABBREV = list(_MONTH_ABBREV_TO_FULL.keys())

_MONTH_FULL = list(_MONTH_ABBREV_TO_FULL.values())

_LOWERCASE_FULL = list(m.lower() for m in _MONTH_FULL)


class MonthLongStringMiddleware(_MonthInterpolator):
    """Replace month numbers with full month names.

    Note that this may be used before or after removing the enclosing,
    but the semantics are different: Enclosed values (e.g. '{jan}', '"jan"' or '"1"')
    will not be transformed. If you want to transform these values, you should
    use this middleware after the RemoveEnclosingMiddleware.

    Full names returned by this middleware are always capitalized
    and unenclosed."""

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "MonthLongStringMiddleware"

    # docstr-coverage: inherited
    def resolve_month_field_val(self, month_field: Field):
        v = month_field.value
        if isinstance(v, str) and v.isdigit():
            v = int(v)
        if isinstance(v, int):
            if v < 1 or v > 12:
                return (
                    month_field,
                    f"month-field unchanged - unknown month {v}",
                )  # Nothing we can do here
            return _MONTH_FULL[v - 1], "transformed int-month to str-month"
        elif isinstance(v, str):
            v_lower = v.lower()

            if v_lower in _MONTH_ABBREV_TO_FULL:
                return (
                    _MONTH_ABBREV_TO_FULL[v_lower],
                    "transformed abbreviated month to full month",
                )
            elif v_lower in _LOWERCASE_FULL:
                default_casing = _MONTH_ABBREV_TO_FULL[v_lower[:3]]
                if v != default_casing:
                    return default_casing, "transformed month casing"

        # We can't do anything else here
        return month_field.value, "month field unchanged"


class MonthAbbreviationMiddleware(_MonthInterpolator):
    """Replace month values with month abbreviations.

    Note that this may be used before or after removing the enclosing,
    but the semantics are different: Enclosed values (e.g. '{jan}', '"jan"' or '"1"')
    will not be transformed. If you want to transform these values, you should
    use this middleware after the RemoveEnclosingMiddleware.

    The created abbreviations are always lowercase and unenclosed."""

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "MonthAbbreviationMiddleware"

    # docstr-coverage: inherited
    def resolve_month_field_val(self, month_field: Field):
        v = month_field.value
        if isinstance(v, str) and v.isdigit():
            v = int(v)
        if isinstance(v, int):
            if v < 1 or v > 12:
                # Nothing we can do here
                return month_field, f"month-field unchanged - unknown month {v}"
            return _MONTH_ABBREV[v - 1], "transformed int-month to abbreviated month"
        elif isinstance(v, str):
            v_lower = v.lower()
            if v_lower in _LOWERCASE_FULL:
                return v_lower[:3], "transformed full month to abbreviated month"
            elif v_lower in _MONTH_ABBREV and not v_lower == v:
                return v_lower, "use lowercase month abbreviation"

        return month_field.value, "month field unchanged"


class MonthIntMiddleware(_MonthInterpolator):
    """Replace month values with month numbers.

    Note that this may be used before or after removing the enclosing,
    but the semantics are different: Enclosed values (e.g. '{jan}', '"jan"' or '"1"')
    will not be transformed. If you want to transform these values, you should
    use this middleware after the RemoveEnclosingMiddleware.

    The created int-months are always integers and unenclosed."""

    # docstr-coverage: inherited
    @classmethod
    def metadata_key(cls) -> str:
        return "MonthIntMiddleware"

    # docstr-coverage: inherited
    def resolve_month_field_val(self, month_field: Field):
        v = month_field.value
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in _MONTH_ABBREV:
                return (
                    _MONTH_ABBREV.index(v_lower[:3]) + 1,
                    "transformed full month to int-month",
                )
            elif v_lower in _LOWERCASE_FULL:
                return (
                    _LOWERCASE_FULL.index(v_lower) + 1,
                    "transformed abbreviated month to int-month",
                )

        if isinstance(v, str) and v.isdigit():
            if 1 <= int(v) <= 12:
                return int(v), "cast month int-string to int"

        return month_field.value, "month field unchanged"
