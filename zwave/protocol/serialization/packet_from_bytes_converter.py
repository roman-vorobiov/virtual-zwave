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
from typing import List, Dict, Optional, Union


class PacketFromBytesConverter(Visitor):
    def __init__(self):
        self.schema: Optional[PacketSchema] = None
        self.data: List[int] = []
        self.idx = 0
        self.list_lengths: Dict[str, int] = {}

    def create_packet(self, schema: PacketSchema, data: List[int]) -> Packet:
        self.schema = schema
        self.data = data
        self.idx = 0
        self.list_lengths = {}

        return Packet(self.schema.name, **dict(self.collect_fields()))

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
        end = self.get_list_end(field)
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
        self.list_lengths[field.field_name] = self.data[self.idx] - field.offset
        self.idx += 1

    @visit(ListField)
    def visit_list_field(self, field: ListField):
        begin = self.idx
        end = self.get_list_end(field)
        yield field.name, self.data[begin:end]
        self.idx = end

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField):
        value = self.data[self.idx]
        current_idx = self.idx

        for mask, subfield in field.subfields.items():
            self.data[self.idx] = value & mask
            yield from self.visit(subfield)
            self.idx = current_idx

        self.data[self.idx] = value
        self.idx += 1

    def get_list_end(self, field: Union[ListField, StringField]):
        # Size of the field is specified by value of another field
        if (length := self.list_lengths.get(field.name)) is not None:
            return self.idx + length

        # Current field is not the last one - calculate the length of the rest
        elif (field_idx := self.schema.fields.index(field)) != len(self.schema.fields) - 1:
            rest_length = sum(pampy.match(field,
                                          IntField, lambda f: f.size,
                                          default=1)
                              for field in self.schema.fields[field_idx + 1:])
            return len(self.data) - rest_length

        # Current field is the last one - consume the rest of the packet
        else:
            return len(self.data)
