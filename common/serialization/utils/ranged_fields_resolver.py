from .field_length_getter import FieldLengthGetter, UNSPECIFIED
from ..schema import Schema, ListField
from ..exceptions import SerializationError

from tools import RangeIterator, Visitor, visit

from typing import Union


class RangedFieldsResolver(Visitor):
    def resolve_ranged_fields(self, schema: Schema):
        getter = FieldLengthGetter(schema.fields)

        it = RangeIterator(schema.fields)
        for field in it:
            if getter.get_field_length(field) is UNSPECIFIED and not it.exhausted:
                remaining_length = sum(getter.get_field_length(field) for field in it)
                self.set_field_stop(field, -remaining_length)
                break

    def set_field_stop(self, field: Union[ListField, Schema], stop: int):
        if stop is UNSPECIFIED:
            raise SerializationError(f"Invalid schema field: {field.name}")

        self.visit(field, stop)

    @visit(ListField)
    def set_list_stop(self, field: ListField, stop: int):
        if FieldLengthGetter([]).get_field_length(field.element_type) is UNSPECIFIED:
            raise SerializationError(f"Invalid schema field: '{field.name}'")

        field.stop = stop

    @visit(Schema)
    def set_schema_stop(self, field: Schema, stop: int):
        field.stop = stop
        self.resolve_ranged_fields(field)
