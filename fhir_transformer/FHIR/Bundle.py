from enum import Enum
from inspect import getmembers
from typing import Any

from fhir_transformer.FHIR.Entry import Entry


class BundleType(Enum):
    Batch = 1
    Transaction = 2

    def __getstate__(self):
        if self.value == 1:
            return "batch"
        if self.value == 2:
            return "transaction"


class Bundle:
    resourceType = "Bundle"
    def __init__(self, bundle_type: BundleType, entries: list[Entry]):
        self.type = bundle_type
        self.entry = entries

    def __getstate__(self) -> dict[str, Any]:
        return dict([t for t in getmembers(self) if not(t[0].startswith("_") or callable(t[1]) or t[1] is None or (
                isinstance(t[1], list) and len(t[1]) == 0))])