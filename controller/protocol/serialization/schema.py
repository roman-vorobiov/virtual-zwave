from abc import ABC
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Field(ABC):
    pass


@dataclass
class ConstField(Field):
    value: int


@dataclass
class LengthOfField(Field):
    field_name: str
    offset: int = 0


@dataclass
class CopyOfField(Field):
    field_name: str


@dataclass
class NamedField(Field):
    name: str


@dataclass
class IntField(NamedField):
    size: int = 1


@dataclass
class StringField(NamedField):
    pass


@dataclass
class BoolField(NamedField):
    pass


@dataclass
class ListField(NamedField):
    pass


@dataclass
class MaskedField(Field):
    fields: Dict[int, NamedField]


@dataclass
class Schema(NamedField):
    fields: List[Field]
