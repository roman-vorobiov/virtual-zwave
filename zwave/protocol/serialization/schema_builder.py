from .schema import (
    PacketSchema,
    ConstField,
    IntField,
    BoolField,
    StringField,
    ListField,
    LengthOfField,
    CopyOfField
)
from .exceptions import SerializationError

from tools import Visitor, visit

import pampy


class PacketSchemaBuilder(Visitor):
    def create_schema(self, name: str, data: list) -> PacketSchema:
        return PacketSchema(name, list(self.collect_fields(data)))

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

    @visit(dict)
    def visit_object(self, field: dict):
        if (length_of := field.get('length_of')) is not None:
            return LengthOfField(field_name=length_of, offset=field.get('offset', 0))

        if (copy_of := field.get('copy_of')) is not None:
            return CopyOfField(field_name=copy_of)

        if (type_str := field.get('type')) is not None:
            return pampy.match(
                type_str,
                'str', lambda _: StringField(name=field['name']),
                'bool', lambda _: BoolField(name=field['name']),
                'int', lambda _: IntField(name=field['name'], size=field.get('size', 1))
            )

        raise SerializationError(f"Invalid schema field: {field}")
