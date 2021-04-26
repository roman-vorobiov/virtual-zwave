from ..schema import Field, Schema, MarkerField, ListField
from ..exceptions import SerializationError

from tools import Visitor, visit

from typing import Optional, Type


class MarkerResolver(Visitor):
    def resolve_marker_fields(self, schema: Schema):
        for field in schema.fields:
            self.visit(field, schema)

    @visit(MarkerField)
    def visit_marker(self, field: MarkerField, schema: Schema):
        next_field = self.get_next_field(field, schema)
        if isinstance(next_field, ListField):
            field.separated_field_name = next_field.name
        else:
            raise SerializationError(f"Invalid schema: {schema.name}")

    @visit(ListField)
    def visit_list(self, field: ListField, schema: Schema):
        if isinstance(field.element_type, Schema):
            self.resolve_marker_fields(field.element_type)

    @visit(Schema)
    def visit_schema(self, field: Schema, schema: Schema):
        self.resolve_marker_fields(field)

    def visit_default(self, field: Field, field_type: Type[Field]):
        pass

    @classmethod
    def get_next_field(cls, field: Field, schema: Schema) -> Optional[Field]:
        try:
            idx = schema.fields.index(field)
            return schema.fields[idx + 1]
        except IndexError:
            pass
