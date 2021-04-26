from .schema import (
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

from tools import Object, RangeIterator, Visitor, visit

import itertools
from typing import Dict, Optional, List, Iterator, Tuple, Any, Union


class Context:
    def __init__(self):
        self.field_lengths: Dict[str, int] = {}
        self.list_lengths: Dict[str, int] = {}


class ObjectFromBytesConverter(Visitor):
    def convert(self, schema: Schema, data: List[int]) -> Object:
        return self.create_object(schema, RangeIterator(data))

    def create_object(self, schema: Schema, it: RangeIterator[int]) -> Object:
        return Object(dict(self.collect_fields(schema, it)))

    def collect_fields(self, schema: Schema, it: RangeIterator[int]) -> Iterator[Tuple[str, Any]]:
        context = Context()
        for field in schema.fields:
            yield from self.visit(field, it, context)

    @visit(ConstField, CopyOfField)
    def visit_ignored_field(self, field: Union[ConstField, CopyOfField], it: RangeIterator[int], context: Context):
        next(it)
        yield from []

    @visit(MarkerField)
    def visit_marker_field(self, field: MarkerField, it: RangeIterator[int], context: Context):
        try:
            next(it)
        except StopIteration:
            yield from []

    @visit(IntField)
    def visit_int_field(self, field: IntField, it: RangeIterator[int], context: Context):
        data = it.slice(field.size)
        yield field.name, int.from_bytes(data, byteorder='big')

    @visit(StringField)
    def visit_string_field(self, field: StringField, it: RangeIterator[int], context: Context):
        if field.null_terminated:
            it = itertools.takewhile(lambda byte: byte != 0, it)

        data = bytes(it)
        yield field.name, data.decode('utf-8')

    @visit(BoolField)
    def visit_bool_field(self, field: BoolField, it: RangeIterator[int], context: Context):
        yield field.name, bool(next(it))

    @visit(LengthOfField)
    def visit_length_of_field(self, field: LengthOfField, it: RangeIterator[int], context: Context):
        context.field_lengths[field.field_name] = next(it) - field.offset
        yield from []

    @visit(NumberOfField)
    def visit_number_of_field(self, field: LengthOfField, it: RangeIterator[int], context: Context):
        context.list_lengths[field.field_name] = next(it)
        yield from []

    @visit(ListField)
    def visit_list_field(self, field: ListField, it: RangeIterator[int], context: Context):
        def stop_mark_reached():
            return field.stop_mark is not None and it.current() == field.stop_mark

        def elements():
            while not (it.exhausted or stop_mark_reached()):
                (_, value), *_ = list(self.visit(field.element_type, it, Context()))
                yield value

        it = it.slice(self.get_length(field, context))
        yield field.name, list(itertools.islice(elements(), context.list_lengths.get(field.name)))

    @visit(MaskedField)
    def visit_masked_field(self, field: MaskedField, it: RangeIterator[int], context: Context):
        value = next(it)
        for mask, subfield in field.fields.items():
            # Todo: handle multi-byte masks
            yield from self.visit(subfield, RangeIterator([value & mask]), context)

    @visit(Schema)
    def visit_composite_field(self, field: Schema, it: RangeIterator[int], context: Context):
        if (length := self.get_length(field, context)) != 0:
            yield field.name, self.create_object(field, it.slice(length))

    @classmethod
    def get_length(cls, field: Union[ListField, Schema], context: Context) -> Optional[int]:
        return field.length or field.stop or context.field_lengths.get(field.name)
