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
from typing import TYPE_CHECKING, List, Dict, Optional, Union

if TYPE_CHECKING:
    from .packet_serializer import PacketSerializer
    from .command_class_serializer import CommandClassSerializer


class ObjectFromBytesConverter(Visitor):
    def __init__(self):
        self.schema: Optional[Schema] = None
        self.data: List[int] = []
        self.idx = 0
        self.field_lengths: Dict[str, int] = {}

    def reset(self, schema: Schema, data: List[int]):
        self.schema = schema
        self.data = data
        self.idx = 0
        self.field_lengths = {}

    def create_object(self, schema: Schema, data: List[int]) -> Object:
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

    @visit(Schema)
    def visit_composite_field(self, field: Schema):
        begin = self.idx
        end = self.idx + self.get_field_length(field)
        if begin != end:
            converter = self.new_instance()
            yield field.name, converter.create_object(field, self.data[begin:end])
            self.idx += converter.idx

    def new_instance(self):
        return ObjectFromBytesConverter()

    def get_field_length(self, field: Union[ListField, StringField, Schema, ObjectField]):
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


class PacketFromBytesConverter(ObjectFromBytesConverter):
    def __init__(self, serializer: 'PacketSerializer'):
        super().__init__()
        self.serializer = serializer

    @visit(ObjectField)
    def visit_object_field(self, field: ObjectField):
        begin = self.idx
        end = self.idx + self.get_field_length(field)
        yield field.name, self.serializer.from_bytes(self.data[begin:end])
        self.idx = end

    def new_instance(self):
        return PacketFromBytesConverter(self.serializer)


class CommandClassFromBytesConverter(ObjectFromBytesConverter):
    def __init__(self, serializer: 'CommandClassSerializer', class_versions: Dict[int, int]):
        super().__init__()
        self.serializer = serializer
        self.class_versions = class_versions

    @visit(ObjectField)
    def visit_object_field(self, field: ObjectField):
        begin = self.idx
        end = self.idx + self.get_field_length(field)
        yield field.name, self.serializer.from_bytes(self.data[begin:end], self.class_versions)
        self.idx = end

    def new_instance(self):
        return CommandClassFromBytesConverter(self.serializer, self.class_versions)
