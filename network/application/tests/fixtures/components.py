from network.application import Node, Channel, ChannelFactory

from controller.protocol.serialization import CommandClassSerializer

from tools import Mock, load_yaml

import pytest


@pytest.fixture
def command_class_serializer():
    schema_files = [
        "controller/protocol/command_classes/management.yaml",
        "controller/protocol/command_classes/transport_encapsulation.yaml",
        "controller/protocol/command_classes/application.yaml"
    ]

    data = {}
    for schema_file in schema_files:
        data.update(load_yaml(schema_file))

    yield CommandClassSerializer(data)


@pytest.fixture
def channel_factory(command_class_serializer):
    yield ChannelFactory(command_class_serializer)


@pytest.fixture
def node():
    Channel.send_command = Mock()

    node = Node(Mock(), basic=0x04)
    node.add_to_network(123, 2)
    yield node


@pytest.fixture
def make_channel(node, channel_factory):
    def inner(generic=0x10, specific=0x01):
        return channel_factory.create_channel(node, generic, specific)

    yield inner


@pytest.fixture
def channel(make_channel):
    yield make_channel()
