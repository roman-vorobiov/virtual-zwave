from ..schema_builder import SchemaBuilder
from ..exceptions import SerializationError
from ..schema import (
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
    assert schema.fields == [StringField(name="hello", null_terminated=False)]


def test_null_terminated_str_field(factory):
    schema = factory.create_schema("", [{'name': "hello", 'type': 'str', 'null_terminated': True}])
    assert schema.fields == [StringField(name="hello", null_terminated=True)]


def test_bool_field(factory):
    schema = factory.create_schema("", [{'name': "hello", 'type': 'bool'}])
    assert schema.fields == [BoolField(name="hello")]


def test_list_field(factory):
    schema = factory.create_schema("", ["hello[]"])
    assert schema.fields == [ListField(name="hello")]


def test_list_field_with_length(factory):
    schema = factory.create_schema("", [{'name': "hello[]", 'length': 8}])
    assert schema.fields == [ListField(name="hello", length=8)]


def test_list_field_in_the_middle(factory):
    schema = factory.create_schema("", ["hello[]", {'name': "tail", 'type': 'int', 'size': 4}])
    assert schema.fields == [ListField(name="hello", stop=-4), IntField(name="tail", size=4)]


def test_list_of_int_field(factory):
    schema = factory.create_schema("", [{'name': "hello[]", 'type': 'int', 'size': 4}])
    assert schema.fields == [ListField(name="hello", element_type=IntField(name="_", size=4))]


def test_list_of_composite_field(factory):
    schema = factory.create_schema("", [{'name': "hello[]", 'schema': ["a", "b"]}])
    assert schema.fields == [
        ListField(name="hello", element_type=Schema(name="_", fields=[IntField(name="a"), IntField(name="b")]))
    ]


def test_list_of_invalid_composite_field_in_the_middle(factory):
    with pytest.raises(SerializationError):
        factory.create_schema("", [
            {'name': "outer[]", 'schema': [
                "inner[]",
                {'name': "tail", 'type': 'int', 'size': 4}
            ]},
            {'name': "tail", 'type': 'int', 'size': 2}
        ])


def test_nested_list_field(factory):
    schema = factory.create_schema("", [{'name': "outer[]", 'schema': [{'length_of': "inner"}, "inner[]"]}])
    assert schema.fields == [
        ListField(name="outer", element_type=Schema(name="_", fields=[
            LengthOfField(field_name="inner"),
            ListField(name="inner")
        ]))
    ]


def test_list_with_stop_mark(factory):
    schema = factory.create_schema("", ["head[]", {'marker': 123}, "tail[]"])
    assert schema.fields == [
        ListField(name="head", stop_mark=123),
        MarkerField(value=123, separated_field_name="tail"),
        ListField(name="tail")
    ]


def test_length_of_field(factory):
    schema = factory.create_schema("", [{'length_of': "hello"}])
    assert schema.fields == [LengthOfField(field_name="hello")]


def test_length_of_field_with_offset(factory):
    schema = factory.create_schema("", [{'length_of': "hello", 'offset': 123}])
    assert schema.fields == [LengthOfField(field_name="hello", offset=123)]


def test_number_of_field(factory):
    schema = factory.create_schema("", [{'number_of': "hello"}])
    assert schema.fields == [NumberOfField(field_name="hello")]


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


def test_composite_field_with_list_at_the_end(factory):
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
        Schema(name="b", stop=-1, fields=[
            IntField(name="b1"),
            ListField(name="b2")
        ]),
        IntField(name="c")
    ]


def test_composite_field__with_list_at_the_front(factory):
    schema = factory.create_schema("", [
        "a",
        {
            'name': "b",
            'schema': ["b1[]", "b2"]
        },
        "c"
    ])
    assert schema.fields == [
        IntField(name="a"),
        Schema(name="b", stop=-1, fields=[
            ListField(name="b1", stop=-1),
            IntField(name="b2")
        ]),
        IntField(name="c")
    ]


def test_multiple_composite_fields_with_lists(factory):
    with pytest.raises(SerializationError):
        factory.create_schema("", [
            {'name': "a", 'schema': ["a1[]"]},
            {'name': "b", 'schema': ["b1[]"]}
        ])


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
