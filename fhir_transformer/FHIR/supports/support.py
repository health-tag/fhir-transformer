from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable

T = TypeVar("T")


@dataclass
class Identifier:
    system: str
    value: str

    def get_string_for_reference(self):
        return f"{self.system}|{self.value}"


class Coding:
    def __init__(self, system: str, code: str, display: str = None):
        self.system = system
        self.code = code
        if display is not None:
            self.display = display

    def get_string_for_reference(self):
        return f"{self.system}|{self.code}"


class Builder(ABC, Generic[T]):
    def __init__(self, factory: Callable[[None], T]):
        self._product: T = None
        self._factory = factory
        self.reset()

    def reset(self):
        self._product = self._factory()
        return self

    @property
    def product(self):
        product = self._product
        self.reset()
        return product

    @property
    def productWithoutReset(self):
        product = self._product
        return product
