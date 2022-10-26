from abc import abstractmethod, ABCMeta
from typing import Any
from inspect import getmembers

import jsonpickle


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


"""
    def __getstate2__(self) -> dict[str, Any]:
        # Gather class attributes for serialization
        class_json_dict = self.__class__.__dict__.copy()
        # print(class_json_dict)
        keys_to_be_deleted = [key for key in class_json_dict if
                              key.startswith("_") or callable(class_json_dict[key]) or class_json_dict[key] is None or (
                                      isinstance(class_json_dict[key], list) and len(class_json_dict[key]) == 0)]
        # print(keys_to_be_deleted)
        for key in keys_to_be_deleted:
            del class_json_dict[key]
        # print(class_json_dict)

        # Gather attributes for serialization
        json_dict = self.__dict__.copy()
        keys_to_be_rename = [key for key in json_dict if key.startswith("_reserved_")]
        for key in keys_to_be_rename:
            json_dict[key[9:]] = json_dict.pop(key)
        keys_to_be_deleted = [key for key in json_dict if key.startswith("_") or json_dict[key] is None or (
                isinstance(json_dict[key], list) and len(json_dict[key]) == 0)]
        for key in keys_to_be_deleted:
            del json_dict[key]

        # Gather properties for serialization
        for name in dir(self.__class__):
            # a protected property is somewhat uncommon but
            # let's stay consistent with plain attribs
            if name.startswith("_"):
                continue
            obj = getattr(self.__class__, name)
            if isinstance(obj, property):
                val = obj.__get__(self, self.__class__)
                if val is not None:
                    json_dict[name] = val

        for key in [key for key in class_json_dict if key in json_dict]:
            del class_json_dict[key]
        print(class_json_dict)

        return {**class_json_dict, **json_dict}
"""
