from .schema_post_processor import SchemaPostProcessor
from .schema import (
    Field,
    NamedField,
    Schema,
    ConstField,
    MarkerField,
    IntField,
    BoolField,
    StringField,
    ListField,
    LengthOfField,
    NumberOfField,
    CopyOfField,
    MaskedField
)

from typing import Dict, Any

import pampy
from pampy import _


class SchemaBuilder:
    def __init__(self):
        self.post_processor = SchemaPostProcessor()

    def create_schema(self, name: str, data: list) -> Schema:
        schema = Schema(name, [self.create_field(field) for field in data])
        self.post_processor.process(schema)
        return schema

    def create_field(self, field: Any) -> Field:
        return pampy.match(
            field,

            int,
            lambda value: ConstField(value=value),

            str,
            lambda name: self.make_named_field(IntField(name=name)),

            Dict[int, Any],
            lambda _: MaskedField(fields={mask: self.create_field(subfield) for mask, subfield in field.items()}),

            {'marker': _},
            lambda marker: MarkerField(value=marker, separated_field_name=""),

            {'length_of': _},
            lambda length_of: LengthOfField(field_name=length_of, offset=field.get('offset', 0)),

            {'number_of': _},
            lambda number_of: NumberOfField(field_name=number_of),

            {'copy_of': _},
            lambda copy_of: CopyOfField(field_name=copy_of),

            {'schema': _, 'name': _},
            lambda schema, name: self.make_named_field(self.create_schema(name, schema)),

            {'type': 'str', 'name': _},
            lambda name: StringField(name=name, null_terminated=field.get('null_terminated', False)),

            {'type': 'bool', 'name': _},
            lambda name: BoolField(name=name),

            {'type': 'int', 'name': _, 'size': _},
            lambda name, size: self.make_named_field(IntField(name=name, size=size)),

            {'name': _, 'length': _},
            lambda name, length: self.make_named_field(IntField(name=name), length)
        )

    @classmethod
    def make_named_field(cls, field: NamedField, length=None) -> NamedField:
        if field.name.endswith("[]"):
            field_name = field.name[:-2]
            field.name = "_"
            return ListField(name=field_name, element_type=field, length=length)
        else:
            return field
