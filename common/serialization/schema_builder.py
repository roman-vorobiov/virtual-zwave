from .schema import (
    NamedField,
    Schema,
    ConstField,
    IntField,
    BoolField,
    StringField,
    ListField,
    LengthOfField,
    NumberOfField,
    CopyOfField,
    MaskedField
)
from .exceptions import SerializationError

from tools import Visitor, visit
from typing import Dict, Any

import pampy


class SchemaBuilder(Visitor):
    def create_schema(self, name: str, data: list) -> Schema:
        return Schema(name, list(self.collect_fields(data)))

    def collect_fields(self, data: list):
        for field in data:
            yield self.visit(field)

    @visit(int)
    def visit_int(self, field: int):
        return ConstField(value=field)

    @visit(str)
    def visit_str(self, field: str):
        return self.make_named_field(IntField(name=field))

    def visit_mask(self, fields: Dict[int, Any]):
        return MaskedField(fields={mask: self.visit(field) for mask, field in fields.items()})

    @visit(dict)
    def visit_object(self, field: dict):
        if type(next(iter(field))) is int:
            return self.visit_mask(field)

        if (length_of := field.get('length_of')) is not None:
            return LengthOfField(field_name=length_of, offset=field.get('offset', 0))

        if (number_of := field.get('number_of')) is not None:
            return NumberOfField(field_name=number_of)

        if (copy_of := field.get('copy_of')) is not None:
            return CopyOfField(field_name=copy_of)

        if (schema := field.get('schema')) is not None:
            return self.make_named_field(self.create_schema(field['name'], schema))

        if (type_str := field.get('type')) is not None:
            return self.make_named_field(pampy.match(
                type_str,
                'str', lambda _: StringField(name=field['name']),
                'bool', lambda _: BoolField(name=field['name']),
                'int', lambda _: IntField(name=field['name'], size=field.get('size', 1))
            ))

        raise SerializationError(f"Invalid schema field: {field}")

    @classmethod
    def make_named_field(cls, field: NamedField) -> NamedField:
        if field.name.endswith("[]"):
            field_name = field.name[:-2]
            field.name = "_"
            return ListField(name=field_name, element_type=field)
        else:
            return field
