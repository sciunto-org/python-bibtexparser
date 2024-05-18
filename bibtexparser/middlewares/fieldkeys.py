import logging
from typing import Dict
from typing import List
from typing import Set

from bibtexparser.library import Library
from bibtexparser.model import Entry
from bibtexparser.model import Field

from .middleware import BlockMiddleware

logger = logging.getLogger(__name__)


class NormalizeFieldKeys(BlockMiddleware):
    """Normalize field keys to lowercase.

    In case of conflicts (e.g. both 'author' and 'Author' exist in the same entry),
    a warning is emitted, and the last value wins.

    Some other middlewares, such as `SeparateCoAuthors`, assume lowercase key names.
    """

    def __init__(self, allow_inplace_modification: bool = True):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: "Library") -> Entry:
        seen_normalized_keys: Set[str] = set()
        new_fields_dict: Dict[str, Field] = {}
        for field in entry.fields:
            normalized_key: str = field.key.lower()
            # if the normalized key is already present, apply "last one wins"
            # otherwise preserve insertion order
            # if a key is overwritten, emit a detailed warning
            # if performance is a concern, we could emit a warning with only {entry.key}
            # to remove "seen_normalized_keys" and this if statement
            if normalized_key in seen_normalized_keys:
                logger.warning(
                    f"NormalizeFieldKeys: in entry '{entry.key}': "
                    + f"duplicate normalized key '{normalized_key}' "
                    + f"(original '{field.key}'); overriding previous value"
                )
            seen_normalized_keys.add(normalized_key)
            field.key = normalized_key
            new_fields_dict[normalized_key] = field

        new_fields: List[Field] = list(new_fields_dict.values())
        entry.fields = new_fields

        return entry
