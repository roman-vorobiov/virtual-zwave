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

from tools import Object, Visitor, visit, until_exhausted

import itertools
from typing import Dict, Optional, Iterable, Iterator, Tuple, Any


class Context:
    def __init__(self):
        self.field_lengths: Dict[str, int] = {}
        self.list_lengths: Dict[str, int] = {}


class ObjectFromBytesConverter(Visitor):
    def create_object(self, schema: Schema, data: Iterable[int]) -> Object:
        return Object(dict(self.collect_fields(schema, iter(data), Context())))

    def collect_fields(self, schema: Schema, it: Iterator[int], context: Context) -> Iterator[Tuple[str, Any]]:
        for field in schema.fields:
            yield from self.visit(field, it, context)

    @visit(ConstField, CopyOfField)
    def visit_const_field(self, field: ConstField, it: Iterator[int], context: Context):
        next(it)
        yield from []

    @visit(IntField)
    def visit_int_field(self, field: IntField, it: Iterator[int], context: Context):
        data = list(itertools.islice(it, field.size))
        yield field.name, int.from_bytes(data, byteorder='big')

    @visit(StringField)
    def visit_string_field(self, field: StringField, it: Iterator[int], context: Context):
        data = bytes(itertools.takewhile(lambda byte: byte != 0, it))
        yield field.name, data.decode('utf-8')

    @visit(BoolField)
    def visit_bool_field(self, field: BoolField, it: Iterator[int], context: Context):
        yield field.name, bool(next(it))

    @visit(LengthOfField)
    def visit_length_of_field(self, field: LengthOfField, it: Iterator[int], context: Context):
        context.field_lengths[field.field_name] = next(it) - field.offset
        yield from []

    @visit(NumberOfField)
    def visit_number_of_field(self, field: LengthOfField, it: Iterator[int], context: Context):
        context.list_lengths[field.field_name] = next(it)
        yield from []

    @visit(ListField)
    def visit_list_field(self, field: ListField, it: Iterator[int], context: Context):
        def element(iterator: Iterator):
            return [value for _, value in self.visit(field.element_type, iterator, Context())][0]

        it = self.get_range(field.name, it, context)
        yield field.name, [element(i) for i in until_exhausted(it, context.list_lengths.get(field.name))]

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField, it: Iterator[int], context: Context):
        value = next(it)
        for mask, subfield in field.fields.items():
            # Todo: handle multi-byte masks
            yield from self.visit(subfield, iter((value & mask,)), context)

    @visit(Schema)
    def visit_composite_field(self, field: Schema, it: Iterator[int], context: Context):
        if (it := self.get_range(field.name, it, context)) is not None:
            yield field.name, self.create_object(field, it)

    @classmethod
    def get_range(cls, field_name: str, it: Iterator[int], context: Context) -> Optional[Iterator[int]]:
        length = context.field_lengths.get(field_name)
        if length is None:
            return it
        elif length != 0:
            return itertools.islice(it, length)
