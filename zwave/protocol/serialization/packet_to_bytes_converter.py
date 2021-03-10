from ..packet import Packet
from .schema import (
    PacketSchema,
    ConstField,
    IntField,
    BoolField,
    StringField,
    ListField,
    LengthOfField,
    CopyOfField,
    MaskedField
)

from tools import Visitor, visit

import pampy
from typing import List, Union, Any


class PacketToBytesConverter(Visitor):
    def serialize_packet(self, schema: PacketSchema, packet: Packet) -> List[int]:
        return list(self.collect_bytes(schema, packet))

    def collect_bytes(self, schema: PacketSchema, packet: Packet):
        for field in schema.fields:
            yield from self.visit(field, packet)

    @visit(ConstField)
    def visit_const_field(self, field: ConstField, packet: Packet):
        yield field.value

    @visit(IntField)
    def visit_int_field(self, field: IntField, packet: Packet):
        yield from packet[field.name].to_bytes(field.size, byteorder='big')

    @visit(StringField)
    def visit_string_field(self, field: StringField, packet: Packet):
        # Manually null-terminate
        yield from [*packet[field.name].encode('utf-8'), 0x00]

    @visit(BoolField)
    def visit_bool_field(self, field: BoolField, packet: Packet):
        yield int(packet[field.name])

    @visit(LengthOfField)
    def visit_length_of_field(self, field: LengthOfField, packet: Packet):
        yield self.get_field_length(packet[field.field_name]) + field.offset

    @visit(ListField)
    def visit_list_field(self, field: ListField, packet: Packet):
        yield from packet[field.name]

    @visit(CopyOfField)
    def visit_copy_of_field(self, field: CopyOfField, packet: Packet):
        yield packet[field.field_name]

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField, packet: Packet):
        value = 0
        for mask, subfield in field.fields.items():
            value |= pampy.match(subfield,
                                 BoolField, lambda _: packet[subfield.name] and mask,
                                 default=packet[subfield.name])

        yield value

    @visit(PacketSchema)
    def visit_composite_field(self, field: PacketSchema, packet: Packet):
        if (subfield := packet[field.name]) is not None:
            yield from self.collect_bytes(field, subfield)

    def get_field_length(self, field: Any):
        return pampy.match(field,
                           Union[list, str], lambda f: len(f),
                           Packet, lambda f: sum(self.get_field_length(subfield) for subfield in f.fields.values()),
                           None, 0,
                           default=1)
