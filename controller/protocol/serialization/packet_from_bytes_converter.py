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

from tools import Object, Visitor, visit

import pampy
from typing import List, Dict, Optional, Union


class PacketFromBytesConverter(Visitor):
    def __init__(self):
        self.schema: Optional[PacketSchema] = None
        self.data: List[int] = []
        self.idx = 0
        self.field_lengths: Dict[str, int] = {}

    def reset(self, schema: PacketSchema, data: List[int]):
        self.schema = schema
        self.data = data
        self.idx = 0
        self.field_lengths = {}

    def create_packet(self, schema: PacketSchema, data: List[int]) -> Packet:
        packet = self.create_object(schema, data)
        packet.set_meta('name', self.schema.name)
        return packet

    def create_object(self, schema: PacketSchema, data: List[int]) -> Object:
        self.reset(schema, data)
        return Object(dict(self.collect_fields()))

    def collect_fields(self):
        for field in self.schema.fields:
            yield from self.visit(field)

    @visit(ConstField, CopyOfField)
    def visit_const_field(self, field: ConstField):
        yield from []
        self.idx += 1

    @visit(IntField)
    def visit_int_field(self, field: IntField):
        yield field.name, int.from_bytes(self.data[self.idx:self.idx + field.size], byteorder='big')
        self.idx += field.size

    @visit(StringField)
    def visit_string_field(self, field: StringField):
        begin = self.idx
        end = self.idx + self.get_field_length(field)
        # Note: ignore null termination
        yield field.name, bytes(self.data[begin:end - 1]).decode('utf-8')
        self.idx = end

    @visit(BoolField)
    def visit_bool_field(self, field: BoolField):
        yield field.name, bool(self.data[self.idx])
        self.idx += 1

    @visit(LengthOfField)
    def visit_length_of_field(self, field: LengthOfField):
        yield from []
        self.field_lengths[field.field_name] = self.data[self.idx] - field.offset
        self.idx += 1

    @visit(ListField)
    def visit_list_field(self, field: ListField):
        begin = self.idx
        end = self.idx + self.get_field_length(field)
        yield field.name, self.data[begin:end]
        self.idx = end

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField):
        value = self.data[self.idx]
        current_idx = self.idx

        for mask, subfield in field.fields.items():
            self.data[self.idx] = value & mask
            yield from self.visit(subfield)
            self.idx = current_idx

        self.data[self.idx] = value
        self.idx += 1

    @visit(PacketSchema)
    def visit_composite_field(self, field: PacketSchema):
        begin = self.idx
        end = self.idx + self.get_field_length(field)
        if begin != end:
            converter = PacketFromBytesConverter()
            yield field.name, converter.create_object(field, self.data[begin:end])
            self.idx += converter.idx

    def get_field_length(self, field: Union[ListField, StringField, PacketSchema]):
        # Size of the field is specified by value of another field
        if (length := self.field_lengths.get(field.name)) is not None:
            return length

        # Current field is not the last one - calculate the length of the rest
        elif (field_idx := self.schema.fields.index(field)) != len(self.schema.fields) - 1:
            rest_length = sum(pampy.match(field,
                                          IntField, lambda f: f.size,
                                          default=1)
                              for field in self.schema.fields[field_idx + 1:])
            return len(self.data) - self.idx - rest_length

        # Current field is the last one - consume the rest of the packet
        else:
            return len(self.data) - self.idx
