from ..object_from_bytes_converter import ObjectFromBytesConverter
from ..object_to_bytes_converter import ObjectToBytesConverter
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

from tools import make_object

import pytest


@pytest.fixture
def from_bytes_converter():
    yield ObjectFromBytesConverter()


@pytest.fixture
def to_bytes_converter():
    yield ObjectToBytesConverter()


def test_const_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [ConstField(value=1)])
    data = [0x01]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.get_data() == {}

    assert to_bytes_converter.convert(schema, packet) == data


def test_extra_field(to_bytes_converter):
    schema = Schema("", [IntField(name="hello")])
    data = [0x11]

    packet = make_object(hello=0x11, bye=0x22)
    assert to_bytes_converter.convert(schema, packet) == data


def test_int_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [IntField(name="hello")])
    data = [0x11]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.hello == 0x11

    assert to_bytes_converter.convert(schema, packet) == data


def test_int_field_with_size(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [IntField(name="hello", size=2)])
    data = [0x01, 0x02]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.hello == 0x0102

    assert to_bytes_converter.convert(schema, packet) == data


def test_str_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [StringField(name="hello", null_terminated=False)])
    data = list(b'hello world')

    packet = from_bytes_converter.convert(schema, data)
    assert packet.hello == "hello world"

    assert to_bytes_converter.convert(schema, packet) == data


def test_null_terminated_str_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [StringField(name="hello", null_terminated=True)])
    data = list(b'hello world\0')

    packet = from_bytes_converter.convert(schema, data)
    assert packet.hello == "hello world"

    assert to_bytes_converter.convert(schema, packet) == data


def test_bool_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [BoolField(name="hello"), BoolField(name="bye")])
    data = [0x00, 0x01]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.hello is False
    assert packet.bye is True

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [ListField(name="command")])
    data = [0x01, 0x02, 0x03, 0x04]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.command == [0x01, 0x02, 0x03, 0x04]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field_in_the_middle(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        IntField(name="head"),
        ListField(name="command", stop=-2),
        IntField(name="tail", size=2)
    ])
    data = [0x01, 0x02, 0x03, 0x04, 0x05]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == 0x01
    assert packet.command == [0x02, 0x03]
    assert packet.tail == 0x0405

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_of_ints_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [ListField(name="values", element_type=IntField(name="_", size=2))])
    data = [0x01, 0x02, 0x03, 0x04]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.values == [0x0102, 0x0304]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_of_composites_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        NumberOfField(field_name="commands"),
        ListField(name="commands", element_type=Schema("_", [
            LengthOfField(field_name="command"),
            ListField(name="command")
        ]))
    ])
    data = [0x03, 0x01, 0x0A, 0x03, 0x0A, 0x0B, 0x0C, 0x02, 0x0A, 0x0B]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.commands == [
        make_object(command=[0x0A]),
        make_object(command=[0x0A, 0x0B, 0x0C]),
        make_object(command=[0x0A, 0x0B]),
    ]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field_with_length_of(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        LengthOfField(field_name="command1", offset=5),
        ListField(name="command1"),
        LengthOfField(field_name="command2"),
        ListField(name="command2"),
        LengthOfField(field_name="command3"),
        ListField(name="command3")
    ])
    data = [0x07, 0x02, 0x03, 0x00, 0x03, 0x05, 0x06, 0x07]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.command1 == [0x02, 0x03]
    assert packet.command2 == []
    assert packet.command3 == [0x05, 0x06, 0x07]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field_with_length(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        ListField(name="command1", length=2),
        ListField(name="command2", length=1),
        ListField(name="command3", length=3)
    ])
    data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.command1 == [0x01, 0x02]
    assert packet.command2 == [0x03]
    assert packet.command3 == [0x04, 0x05, 0x06]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field_with_stop_marker(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        ListField(name="head", stop_mark=0x00),
        MarkerField(value=0x00, separated_field_name="tail"),
        ListField(name="tail")
    ])
    data = [0x01, 0x02, 0x00, 0x04, 0x05, 0x06]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == [0x01, 0x02]
    assert packet.tail == [0x04, 0x05, 0x06]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field_with_stop_marker_at_the_front(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        ListField(name="head", stop_mark=0x00),
        MarkerField(value=0x00, separated_field_name="tail"),
        ListField(name="tail")
    ])
    data = [0x00, 0x04, 0x05, 0x06]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == []
    assert packet.tail == [0x04, 0x05, 0x06]

    assert to_bytes_converter.convert(schema, packet) == data


def test_list_field_with_stop_marker_at_the_end(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        ListField(name="head", stop_mark=0x00),
        MarkerField(value=0x00, separated_field_name="tail"),
        ListField(name="tail")
    ])
    data = [0x01, 0x02]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == [0x01, 0x02]
    assert packet.tail == []

    assert to_bytes_converter.convert(schema, packet) == data


def test_copy_of_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [IntField(name="hello"), CopyOfField(field_name="hello")])
    data = [0x01, 0x01]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.hello == 0x01

    assert to_bytes_converter.convert(schema, packet) == data


def test_masked_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        IntField(name="head"),
        MaskedField(fields={
            0b00000111: IntField(name="lsb"),
            0b00010000: BoolField(name="flag"),
            0b11000000: IntField(name="msb")
        }),
        IntField(name="tail")
    ])
    data = [0x01, 0b00010011, 0x02]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == 0x01
    assert packet.lsb == 0x03
    assert packet.flag is True
    assert packet.msb == 0x00
    assert packet.tail == 0x02

    assert to_bytes_converter.convert(schema, packet) == data


def test_composite_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        IntField(name="head"),
        Schema(name="data", fields=[
            IntField(name="head"),
            ListField(name="tail")
        ])
    ])
    data = [0x01, 0x02, 0x03, 0x04]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == 0x01
    assert packet.data.head == 0x02
    assert packet.data.tail == [0x03, 0x04]

    assert to_bytes_converter.convert(schema, packet) == data


def test_composite_field_with_length(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        IntField(name="head"),
        LengthOfField(field_name="data"),
        Schema(name="data", stop=-1, fields=[
            IntField(name="head"),
            ListField(name="tail")
        ]),
        IntField(name="tail")
    ])
    data = [0x01, 0x03, 0x02, 0x03, 0x04, 0x05]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == 0x01
    assert packet.data.head == 0x02
    assert packet.data.tail == [0x03, 0x04]
    assert packet.tail == 0x05

    assert to_bytes_converter.convert(schema, packet) == data


def test_empty_composite_field(from_bytes_converter, to_bytes_converter):
    schema = Schema("", [
        IntField(name="head"),
        LengthOfField(field_name="data"),
        Schema(name="data", fields=[
            IntField(name="head"),
            ListField(name="tail")
        ]),
        IntField(name="tail")
    ])
    data = [0x01, 0x00, 0x02]

    packet = from_bytes_converter.convert(schema, data)
    assert packet.head == 0x01
    assert packet.tail == 0x02

    assert to_bytes_converter.convert(schema, packet) == data
