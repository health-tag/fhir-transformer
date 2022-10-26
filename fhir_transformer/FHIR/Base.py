from abc import abstractmethod, ABCMeta
from typing import Any
from inspect import getmembers

class FHIRResource(metaclass=ABCMeta):
    def __init__(self, resource_type: str):
        self.resourceType = resource_type

    @abstractmethod
    def create_entry(self):
        pass

    @abstractmethod
    def __getstate__(self) -> dict[str, Any]:
        json_dict = dict(
            [t for t in getmembers(self) if
             not ((t[0].startswith("_") and not (t[0].startswith("_reserved_"))) or callable(t[1]) or t[1] is None or (
                     isinstance(t[1], list) and len(t[1]) == 0))])
        keys_to_be_rename = [key for key in json_dict if key.startswith("_reserved_")]
        for key in keys_to_be_rename:
            json_dict[key[10:]] = json_dict.pop(key)
        return json_dict