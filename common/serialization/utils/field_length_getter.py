from ..schema import (
    Field,
    Schema,
    IntField,
    StringField,
    ListField,
    ReferenceField
)

from tools import Visitor, visit

from typing import List, Optional, Union


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
        return DYNAMIC

    def visit_default(self, field: Schema, *args, **kwargs):
        return 1

    def find_reference_field(self, field_name: str) -> Optional[ReferenceField]:
        return next(filter(lambda f: isinstance(f, ReferenceField) and f.field_name == field_name, self.fields), None)
