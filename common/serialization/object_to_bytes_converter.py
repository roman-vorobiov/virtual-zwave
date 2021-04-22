from .schema import (
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

from tools import Object, make_object, Visitor, visit

import pampy
from typing import List, Union, Any


class ObjectToBytesConverter(Visitor):
    def convert(self, schema: Schema, obj: Object) -> List[int]:
        return list(self.collect_bytes(schema, obj))

    def collect_bytes(self, schema: Schema, obj: Object):
        for field in schema.fields:
            yield from self.visit(field, obj)

    @visit(ConstField)
    def visit_const_field(self, field: ConstField, obj: Object):
        yield field.value

    @visit(IntField)
    def visit_int_field(self, field: IntField, obj: Object):
        yield from getattr(obj, field.name).to_bytes(field.size, byteorder='big')

    @visit(StringField)
    def visit_string_field(self, field: StringField, obj: Object):
        yield from getattr(obj, field.name).encode('utf-8')

    @visit(BoolField)
    def visit_bool_field(self, field: BoolField, obj: Object):
        yield int(getattr(obj, field.name))

    @visit(LengthOfField)
    def visit_length_of_field(self, field: LengthOfField, obj: Object):
        yield self.get_field_length(getattr(obj, field.field_name)) + field.offset

    @visit(NumberOfField)
    def visit_number_of_field(self, field: NumberOfField, obj: Object):
        yield len(getattr(obj, field.field_name))

    @visit(ListField)
    def visit_list_field(self, field: ListField, obj: Object):
        for value in getattr(obj, field.name):
            proxy = make_object(_=value)
            yield from self.visit(field.element_type, proxy)

    @visit(CopyOfField)
    def visit_copy_of_field(self, field: CopyOfField, obj: Object):
        yield getattr(obj, field.field_name)

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField, obj: Object):
        value = 0
        for mask, subfield in field.fields.items():
            value |= pampy.match(subfield,
                                 BoolField, lambda _: getattr(obj, subfield.name) and mask,
                                 pampy._, lambda _: next(self.visit(subfield, obj)))

        yield value

    @visit(Schema)
    def visit_composite_field(self, field: Schema, obj: Object):
        if (subfield := getattr(obj, field.name)) is not None:
            yield from self.collect_bytes(field, subfield)

    def get_field_length(self, field: Any):
        return pampy.match(field,
                           [], 0,
                           List[Object], lambda f: sum(self.get_field_length(element) for element in f),
                           Union[List[int], str], lambda f: len(f),
                           Object, lambda f: sum(self.get_field_length(subfield) for subfield in f.get_data().values()),
                           None, 0,
                           default=1)
