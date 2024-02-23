import logging
from typing import Collection, Dict, List, Set, Union

from bibtexparser.library import Library
from bibtexparser.model import Block, Entry, Field

from .middleware import BlockMiddleware


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

    def transform_entry(
        self, entry: Entry, library: "Library"
    ) -> Union[Block, Collection[Block], None]:
        seen_normalized_keys: Set[str] = set()
        new_fields_dict: Dict[str, Field] = {}
        for field in entry.fields:
            normalized_key: str = field.key.lower()
            # Since we always mutate `field` here, we will lose the original key after we normalize it.
            # Upon a key name conflict, checking here allows us to emit a helpful warning that makes it
            # easy to locate the offending key even if the entry is long (some online services include
            # many optional fields into their BibTeX outputs).
            #
            # The other option to produce this helpful error message would be to collect a copy of the
            # original key names, but almost always (no conflicts), they are not needed, so collecting
            # them would only cause unnecessary pressure on the garbage collector.
            #
            # Alternatively, we could just report `entry.key`, not which key or keys were the offending ones,
            # which runs faster, but is not as helpful for the user.
            #
            # Note that maximizing speed here is mainly important in applications where BibTeX parsing takes
            # much of the run time, such as reference database converters. In most other applications,
            # whatever the application does with the imported BibTeX data typically takes orders of magnitude
            # longer than the BibTeX import. For such applications, the better warning message is more important.
            if normalized_key in seen_normalized_keys:
                logging.warning(
                    f"NormalizeFieldKeys: in entry '{entry.key}': duplicate normalized key '{normalized_key}' (original '{field.key}'); overriding previous value"
                )
            seen_normalized_keys.add(normalized_key)
            field.key = normalized_key
            new_fields_dict[normalized_key] = (
                field  # This implements "last one wins", but otherwise preserves insertion order.
            )

        new_fields: List[Field] = list(new_fields_dict.values())
        entry.fields = new_fields

        return entry
