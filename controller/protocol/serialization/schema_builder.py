from .schema import (
    Schema,
    ConstField,
    IntField,
    BoolField,
    StringField,
    ListField,
    LengthOfField,
    CopyOfField,
    MaskedField,
    ObjectField,
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
        if field.endswith("[]"):
            return ListField(name=field[:-2])
        else:
            return IntField(name=field)

    def visit_mask(self, fields: Dict[int, Any]):
        return MaskedField(fields={mask: self.visit(field) for mask, field in fields.items()})

    @visit(dict)
    def visit_object(self, field: dict):
        if type(next(iter(field))) is int:
            return self.visit_mask(field)

        if (length_of := field.get('length_of')) is not None:
            return LengthOfField(field_name=length_of, offset=field.get('offset', 0))

        if (copy_of := field.get('copy_of')) is not None:
            return CopyOfField(field_name=copy_of)

        if (schema := field.get('schema')) is not None:
            return self.create_schema(field['name'], schema)

        if (type_str := field.get('type')) is not None:
            return pampy.match(
                type_str,
                'str', lambda _: StringField(name=field['name']),
                'bool', lambda _: BoolField(name=field['name']),
                'int', lambda _: IntField(name=field['name'], size=field.get('size', 1)),
                'Object', lambda _: ObjectField(name=field['name'])
            )

        raise SerializationError(f"Invalid schema field: {field}")
