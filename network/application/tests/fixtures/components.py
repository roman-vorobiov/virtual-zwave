from network.application import ChannelFactory

from network.protocol import CommandClassSerializer

from tools import load_yaml

import pytest


@pytest.fixture
def command_class_serializer():
    schema_files = [
        "network/protocol/command_classes/management.yaml",
        "network/protocol/command_classes/transport_encapsulation.yaml",
        "network/protocol/command_classes/application.yaml"
    ]

    data = {}
    for schema_file in schema_files:
        data.update(load_yaml(schema_file))

    yield CommandClassSerializer(data)


@pytest.fixture
def channel_factory(command_class_serializer):
    yield ChannelFactory(command_class_serializer)
