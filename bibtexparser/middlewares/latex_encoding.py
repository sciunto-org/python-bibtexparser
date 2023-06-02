import abc
import logging
import re
from typing import List, Optional, Tuple

import pylatexenc
from pylatexenc.latex2text import LatexNodes2Text, MacroTextSpec
from pylatexenc.latexencode import (
    RULE_REGEX,
    UnicodeToLatexConversionRule,
    UnicodeToLatexEncoder,
)

from bibtexparser.exceptions import PartialMiddlewareException
from bibtexparser.library import Library
from bibtexparser.model import Block, Entry, MiddlewareErrorBlock, String

from .middleware import BlockMiddleware
from .names import NameParts


class _PyStringTransformerMiddleware(BlockMiddleware, abc.ABC):
    """Abstract utility class allowing to modify python-strings"""

    @abc.abstractmethod
    def _transform_python_value_string(self, python_string: str) -> Tuple[str, str]:
        """Called for every python (value, not key) string found on Entry and String blocks.

        Returns:
            - The transformed string, if the transformation was successful
            - An error message, if any, or an empty string
        """
        raise NotImplementedError("called abstract method")

    # docstr-coverage: inherited
    def _transform_all_strings(
        self, list_of_strings: List[str], errors: List[str]
    ) -> List[str]:
        """Called for every python (value, not key) string found on Entry and String blocks"""
        res = []
        for s in list_of_strings:
            r, e = self._transform_python_value_string(s)
            res.append(r)
            errors.append(e)
        return res

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: Library) -> Block:
        errors = []
        for field in entry.fields:
            if isinstance(field.value, str):
                field.value, e = self._transform_python_value_string(field.value)
                errors.append(e)
            elif isinstance(field.value, NameParts):
                field.value.first = self._transform_all_strings(
                    field.value.first, errors
                )
                field.value.last = self._transform_all_strings(field.value.last, errors)
                field.value.von = self._transform_all_strings(field.value.von, errors)
                field.value.jr = self._transform_all_strings(field.value.jr, errors)
            else:
                logging.info(
                    f" [{self.metadata_key()}] Cannot python-str transform field {field.key}"
                    f" with value type {type(field.value)}"
                )

        errors = [e for e in errors if e != ""]
        if len(errors) > 0:
            errors = PartialMiddlewareException(errors)
            return MiddlewareErrorBlock(block=entry, error=errors)
        else:
            return entry

    # docstr-coverage: inherited
    def transform_string(self, string: String, library: "Library") -> Block:
        if isinstance(string.value, str):
            string.value = self._transform_python_value_string(string.value)
        else:
            logging.info(
                f" [{self.metadata_key()}] Cannot python-str transform string {string.key}"
                f" with value type {type(string.value)}"
            )
        return string


class LatexEncodingMiddleware(_PyStringTransformerMiddleware):
    """Latex-Encodes all strings in the library"""

    def __init__(
        self,
        keep_math: bool = None,
        enclose_urls: bool = None,
        encoder: Optional[UnicodeToLatexEncoder] = None,
        allow_inplace_modification: bool = True,
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

        if encoder is not None and (keep_math is not None or enclose_urls is not None):
            raise ValueError(
                "Cannot specify both encoder and keep_math or enclose_urls."
                "If you want to use a custom encoder, you have to specify it completely."
            )

        # Defaults (not specified as defaults in args,
        #   to make sure we can identify if they were specified)
        keep_math = keep_math if keep_math is not None else True
        enclose_urls = enclose_urls if enclose_urls is not None else True

        # Build encoder if no encoder was specified
        if encoder is None:
            conversion_rules = []
            if keep_math is True:
                conversion_rules.append(
                    UnicodeToLatexConversionRule(
                        rule_type=RULE_REGEX,
                        # keep math mode parts as is
                        rule=[(re.compile(r"(?<!\\)(\$.*[^\\]\$)"), r"\1")],
                    )
                )
            if enclose_urls is True:
                conversion_rules.append(
                    UnicodeToLatexConversionRule(
                        rule_type=RULE_REGEX,
                        rule=[
                            (re.compile(r"(https?://\S*\.\S*)"), r"\\url{\1}"),
                            (re.compile(r"(www.\S*\.\S*)"), r"\\url{\1}"),
                        ],
                    )
                )

            conversion_rules.append("defaults")
            encoder = UnicodeToLatexEncoder(conversion_rules=conversion_rules)
        self._encoder = encoder

    # docstr-coverage: inherited
    def metadata_key(self) -> str:
        return "latex_encoding"

    # docstr-coverage: inherited
    def _transform_python_value_string(self, python_string: str) -> Tuple[str, str]:
        try:
            return self._encoder.unicode_to_latex(python_string), ""
        except Exception as e:
            return python_string, str(e)


class LatexDecodingMiddleware(_PyStringTransformerMiddleware):
    """Latex-Decodes all strings in the library"""

    def __init__(
        self,
        allow_inplace_modification: bool = True,
        keep_braced_groups: bool = None,
        keep_math_mode: bool = None,
        decoder: Optional[LatexNodes2Text] = None,
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

        if decoder is not None and (
            keep_braced_groups is not None or keep_math_mode is not None
        ):
            raise ValueError(
                "Cannot specify both encoder and one of "
                "`keep_braced_groups` or `keep_braced_groups`."
                "If you want to use a custom encoder, "
                "you have to specify it completely."
            )

        # Defaults (not specified as defaults in args,
        #   to make sure we can identify if they were specified)
        keep_braced_groups = (
            keep_braced_groups if keep_braced_groups is not None else False
        )
        keep_math_mode = keep_math_mode if keep_math_mode is not None else True

        if decoder is None:
            lw_context_db = pylatexenc.latex2text.get_default_latex_context_db()
            lw_context_db.add_context_category(
                "bibtexparse-default-context",
                prepend=True,
                macros=[
                    # Do not wrap urls in '< ... >'
                    MacroTextSpec("url", simplify_repl="%s")
                ],
            )

            decoder = LatexNodes2Text(
                # Use custom latex context
                latex_context=lw_context_db,
                # Optionally, do not remove curly braces
                keep_braced_groups=keep_braced_groups,
                # Optionally, decode math notation
                math_mode="verbatim" if keep_math_mode is True else "text",
            )

        self._decoder = decoder

    # docstr-coverage: inherited
    def metadata_key(self) -> str:
        return "latex_decoding"

    # docstr-coverage: inherited
    def _transform_python_value_string(self, python_string: str) -> Tuple[str, str]:
        """Transforms a python string to a latex string

        Returns:
            Tuple[str, str]: The transformed string and a possible error message
        """
        try:
            return self._decoder.latex_to_text(python_string), ""
        except Exception as e:
            return python_string, str(e)
