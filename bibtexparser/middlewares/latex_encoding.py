import abc
import logging
from typing import Optional

from pylatexenc import latexencode
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexencode import unicode_to_latex

from bibtexparser.middlewares.middleware import BlockMiddleware
from bibtexparser.middlewares.names import NameParts
from bibtexparser.model import String, Block, Entry


class _PyStringTransformerMiddleware(BlockMiddleware, abc.ABC):
    """Abstract utility class allowing to modify python-strings"""

    @abc.abstractmethod
    def _transform_python_value_string(self, python_string: str) -> str:
        """Called for every python (value, not key) string found on Entry and String blocks"""
        raise NotImplementedError("called abstract method")

    def transform_entry(self, entry: Entry, library: "Library") -> Block:
        for field in entry.fields.values():
            if isinstance(field.value, str):
                field.value = self._transform_python_value_string(field.value)
            elif isinstance(field.value, NameParts):
                field.value.first = [self._transform_python_value_string(f) for f in field.value.first]
                field.value.last = [self._transform_python_value_string(n) for n in field.value.last]
                field.value.von = [self._transform_python_value_string(v) for v in field.value.von]
                field.value.jr = [self._transform_python_value_string(j) for j in field.value.jr]
            else:
                logging.info(f" [{self.metadata_key()}] Cannot python-str transform field {field.key}"
                             f" with value type {type(field.value)}")
        return entry

    def transform_string(self, string: String, library: "Library") -> Block:
        if isinstance(string.value, str):
            string.value = self._transform_python_value_string(string.value)
        else:
            logging.info(f" [{self.metadata_key()}] Cannot python-str transform string {string.key}"
                         f" with value type {type(string.value)}")
        return string


class LatexEncodingMiddleware(_PyStringTransformerMiddleware):
    """Latex-Encodes all strings in the library"""

    def metadata_key(self) -> str:
        return "latex_encoding"

    def _transform_python_value_string(self, python_string: str) -> str:
        return unicode_to_latex(python_string)


class LatexDecodingMiddleware(_PyStringTransformerMiddleware):
    """Latex-Decodes all strings in the library"""

    def __init__(self,
                 allow_inplace_modification: bool,
                 decoder: Optional[LatexNodes2Text] = None):
        super().__init__(allow_inplace_modification, allow_parallel_execution=True)
        if decoder is None:
            decoder = LatexNodes2Text(
                # Do not remove curly braces
                keep_braced_groups=True,
                # Do not remove math formatted stuff (common e.g. in abstracts)
                math_mode='verbatim'
            )

        self._decoder = decoder

    def metadata_key(self) -> str:
        return "latex_decoding"

    def _transform_python_value_string(self, python_string: str) -> str:
        return self._decoder.latex_to_text(python_string)
