from ..schema_builder import PacketSchemaBuilder
from ..schema import (
    ConstField,
    IntField,
    BoolField,
    StringField,
    ListField,
    LengthOfField,
    CopyOfField
)

import pytest


@pytest.fixture
def factory():
    yield PacketSchemaBuilder()


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


def test_length_of_field(factory):
    schema = factory.create_schema("", [{'length_of': "hello"}])
    assert schema.fields == [LengthOfField(field_name="hello")]


def test_length_of_field_with_offset(factory):
    schema = factory.create_schema("", [{'length_of': "hello", 'offset': 123}])
    assert schema.fields == [LengthOfField(field_name="hello", offset=123)]


def test_copy_of_field(factory):
    schema = factory.create_schema("", ["hello", {'copy_of': "hello"}])
    assert schema.fields == [IntField(name="hello"), CopyOfField(field_name="hello")]


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
