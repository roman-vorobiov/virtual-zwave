from ..schema import (
    Field,
    Schema,
    MarkerField,
    IntField,
    StringField,
    ListField,
    ReferenceField
)

from tools import Visitor, visit

from typing import List, Optional, Union, Type


class Unspecified:
    def __add__(self, other):
        return self

    def __radd__(self, other):
        return self

    def __neg__(self):
        return self


class Dynamic:
    def __add__(self, other):
        if isinstance(other, Unspecified):
            return other
        else:
            return self

    def __radd__(self, other):
        return self

    def __neg__(self):
        return self


UNSPECIFIED = Unspecified()
DYNAMIC = Dynamic()


class FieldLengthGetter(Visitor):
    def __init__(self, fields: List[Field]):
        self.fields = fields

    def get_field_length(self, field: Field) -> Union[int, Dynamic, Unspecified]:
        return self.visit(field)

    @visit(ListField)
    def get_list_length(self, field: ListField):
        # Static length is manually specified in the schema
        if field.length is not None:
            return field.length

        # Dynamic length or number of elements is specified in another field
        if self.find_reference_field(field.name) is not None:
            if FieldLengthGetter([]).get_field_length(field.element_type) is not UNSPECIFIED:
                return DYNAMIC

        # Consume packet until the marker
        next_field = self.get_next_field(field)
        if isinstance(next_field, MarkerField):
            field.stop_mark = next_field.value
            return DYNAMIC

        return UNSPECIFIED

    @visit(Schema)
    def get_schema_length(self, field: Schema):
        # Cached
        if (length := field.length) is not None:
            return length

        getter = FieldLengthGetter(field.fields)
        length = sum(getter.get_field_length(subfield) for subfield in field.fields)

        # Dynamic length is specified in another field
        if self.find_reference_field(field.name) is not None:
            if length is not UNSPECIFIED:
                return DYNAMIC

        # Static length can be calculated from subfields - cache it
        if length not in (UNSPECIFIED, DYNAMIC):
            field.length = length

        return length

    @visit(IntField)
    def get_int_length(self, field: IntField):
        return field.size

    @visit(StringField)
    def get_string_length(self, field: StringField):
        if field.null_terminated:
            return DYNAMIC

        if self.find_reference_field(field.name) is not None:
            return DYNAMIC

        return UNSPECIFIED

    def visit_default(self, field: Field, field_type: Type[Field]):
        return 1

    def find_reference_field(self, field_name: str) -> Optional[ReferenceField]:
        return next(filter(lambda f: isinstance(f, ReferenceField) and f.field_name == field_name, self.fields), None)

    def get_next_field(self, field: Field) -> Optional[Field]:
        try:
            idx = self.fields.index(field)
            return self.fields[idx + 1]
        except IndexError:
            pass
