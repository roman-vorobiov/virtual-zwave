from ..schema_builder import SchemaBuilder
from ..schema import (
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

import pytest


@pytest.fixture
def factory():
    yield SchemaBuilder()


def test_const_field(factory):
    schema = factory.create_schema("", [123])
    assert schema.fields == [ConstField(value=123)]


def test_named_field(factory):
    schema = factory.create_schema("", ["hello"])
    assert schema.fields == [IntField(name="hello")]


def test_int_field(factory):
    schema = factory.create_schema("", [{'name': "hello", 'type': 'int', 'size': 4}])
    assert schema.fields == [IntField(name="hello", size=4)]


def test_str_field(factory):
    schema = factory.create_schema("", [{'name': "hello", 'type': 'str'}])
    assert schema.fields == [StringField(name="hello")]


def test_bool_field(factory):
    schema = factory.create_schema("", [{'name': "hello", 'type': 'bool'}])
    assert schema.fields == [BoolField(name="hello")]


def test_list_field(factory):
    schema = factory.create_schema("", ["hello[]"])
    assert schema.fields == [ListField(name="hello")]


def test_list_of_int_field(factory):
    schema = factory.create_schema("", [{'name': "hello[]", 'type': 'int', 'size': 4}])
    assert schema.fields == [ListField(name="hello", element_type=IntField(name="_", size=4))]


def test_list_of_composite_field(factory):
    schema = factory.create_schema("", [{'name': "hello[]", 'schema': ["a", "b"]}])
    assert schema.fields == [
        ListField(name="hello", element_type=Schema(name="_", fields=[IntField(name="a"), IntField(name="b")]))
    ]


def test_nested_list_field(factory):
    schema = factory.create_schema("", [{'name': "outer[]", 'schema': [{'length_of': "inner"}, "inner[]"]}])
    assert schema.fields == [
        ListField(name="outer", element_type=Schema(name="_", fields=[
            LengthOfField(field_name="inner"),
            ListField(name="inner")
        ]))
    ]


def test_length_of_field(factory):
    schema = factory.create_schema("", [{'length_of': "hello"}])
    assert schema.fields == [LengthOfField(field_name="hello")]


def test_number_of_field(factory):
    schema = factory.create_schema("", [{'number_of': "hello"}])
    assert schema.fields == [NumberOfField(field_name="hello")]


def test_length_of_field_with_offset(factory):
    schema = factory.create_schema("", [{'length_of': "hello", 'offset': 123}])
    assert schema.fields == [LengthOfField(field_name="hello", offset=123)]


def test_copy_of_field(factory):
    schema = factory.create_schema("", ["hello", {'copy_of': "hello"}])
    assert schema.fields == [IntField(name="hello"), CopyOfField(field_name="hello")]


def test_masked_field(factory):
    schema = factory.create_schema("", [
        {
            0b00000111: "lsb",
            0b00010000: {'name': "flag", 'type': 'bool'},
            0b11000000: "msb"
        }
    ])
    assert schema.fields == [
        MaskedField(fields={
            0b00000111: IntField(name="lsb"),
            0b00010000: BoolField(name="flag"),
            0b11000000: IntField(name="msb")
        })
    ]


def test_composite_field(factory):
    schema = factory.create_schema("", [
        "a",
        {
            'name': "b",
            'schema': ["b1", "b2[]"]
        },
        "c"
    ])
    assert schema.fields == [
        IntField(name="a"),
        Schema(name="b", fields=[
            IntField(name="b1"),
            ListField(name="b2")
        ]),
        IntField(name="c")
    ]


def test_multiple_fields(factory):
    schema = factory.create_schema("Data", [
        0x01,
        {'length_of': "command", 'offset': 2},
        "type",
        "command[]",
        "checksum"
    ])

    assert schema.name == "Data"

    assert schema.fields == [
        ConstField(value=1),
        LengthOfField(field_name="command", offset=2),
        IntField(name="type"),
        ListField(name="command"),
        IntField(name="checksum")
    ]
