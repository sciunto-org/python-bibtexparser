from bibtexparser.library import Library
from bibtexparser.model import Entry

from .middleware import BlockMiddleware


class NormalizeEntryTypes(BlockMiddleware):
    """Normalize entry-type identifiers to lowercase.

    Parsing preserves the declared spelling by default so a read/write cycle
    does not create case-only changes. Add this middleware when canonical
    lowercase entry types are preferred over source preservation.
    """

    def __init__(self, allow_inplace_modification: bool = True):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    # docstr-coverage: inherited
    def transform_entry(self, entry: Entry, library: Library) -> Entry:
        entry.entry_type = entry.entry_type.lower()
        return entry
