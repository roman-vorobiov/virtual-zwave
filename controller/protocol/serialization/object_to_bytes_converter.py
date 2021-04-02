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
    ObjectField
)

from tools import Object, Visitor, visit

import pampy
from typing import TYPE_CHECKING, List, Union, Any

if TYPE_CHECKING:
    from .packet_serializer import PacketSerializer
    from .command_class_serializer import CommandClassSerializer


class ObjectToBytesConverter(Visitor):
    def __init__(self, serializer: Union['PacketSerializer', 'CommandClassSerializer']):
        self.serializer = serializer

    def serialize_object(self, schema: Schema, obj: Object) -> List[int]:
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
        # Manually null-terminate
        yield from [*getattr(obj, field.name).encode('utf-8'), 0x00]

    @visit(BoolField)
    def visit_bool_field(self, field: BoolField, obj: Object):
        yield int(getattr(obj, field.name))

    @visit(LengthOfField)
    def visit_length_of_field(self, field: LengthOfField, obj: Object):
        yield self.get_field_length(getattr(obj, field.field_name)) + field.offset

    @visit(ListField)
    def visit_list_field(self, field: ListField, obj: Object):
        yield from getattr(obj, field.name)

    @visit(CopyOfField)
    def visit_copy_of_field(self, field: CopyOfField, obj: Object):
        yield getattr(obj, field.field_name)

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField, obj: Object):
        value = 0
        for mask, subfield in field.fields.items():
            value |= pampy.match(subfield,
                                 BoolField, lambda _: getattr(obj, subfield.name) and mask,
                                 default=getattr(obj, subfield.name))

        yield value

    @visit(Schema)
    def visit_composite_field(self, field: Schema, obj: Object):
        if (subfield := getattr(obj, field.name)) is not None:
            yield from self.collect_bytes(field, subfield)

    @visit(ObjectField)
    def visit_object_field(self, field: ObjectField, obj: Object):
        subfield = getattr(obj, field.name)
        yield from self.serializer.to_bytes(subfield)

    def get_field_length(self, field: Any):
        return pampy.match(field,
                           Union[list, str], lambda f: len(f),
                           Object, lambda f: sum(self.get_field_length(subfield) for subfield in f.get_data().values()),
                           None, 0,
                           default=1)


class PacketToBytesConverter(ObjectToBytesConverter):
    pass


class CommandClassToBytesConverter(ObjectToBytesConverter):
    pass
