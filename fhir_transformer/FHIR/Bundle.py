from enum import Enum
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
        self.resourceType = Bundle.resourceType

    def __getstate__(self) -> dict[str, Any]:
        json_dict = self.__dict__.copy()
        return json_dict

    #def create_entry(self, bundle_id: int) -> Entry:
    #    entry = Entry(f"urn:uuid:Bundle/{bundle_id}", self, {
    #        "method": "POST",
    #        "url": f"http://localhost:8080/fhir",
    #    })
    #    return entry
