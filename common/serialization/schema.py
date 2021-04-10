from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Field(ABC):
    pass


@dataclass
class ConstField(Field):
    value: int


@dataclass
class ReferenceField(Field):
    field_name: str


@dataclass
class LengthOfField(ReferenceField):
    offset: int = 0


@dataclass
class NumberOfField(ReferenceField):
    pass


@dataclass
class CopyOfField(ReferenceField):
    pass


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
    element_type: Field = field(default_factory=lambda: IntField(name="_"))
    length: Optional[int] = None
    stop: Optional[int] = None


@dataclass
class MaskedField(Field):
    fields: Dict[int, NamedField]


@dataclass
class Schema(NamedField):
    fields: List[Field]
    length: Optional[int] = None
    stop: Optional[int] = None
