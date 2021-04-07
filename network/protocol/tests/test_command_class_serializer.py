from .fixtures import APPLICATION, MANAGEMENT, TRANSPORT_ENCAPSULATION

from network.protocol import CommandClassSerializer

from tools import load_yaml

import pytest


@pytest.fixture(scope='session')
def serializer():
    schema_files = [
        "network/protocol/command_classes/management.yaml",
        "network/protocol/command_classes/transport_encapsulation.yaml",
        "network/protocol/command_classes/application.yaml"
    ]

    data = {}
    for schema_file in schema_files:
        data.update(load_yaml(schema_file))

    yield CommandClassSerializer(data)


@pytest.mark.parametrize("data,expected", [*APPLICATION, *MANAGEMENT, *TRANSPORT_ENCAPSULATION])
def test_serialization(serializer, data, expected):
    command = serializer.from_bytes(data, expected.get_meta('class_version'))
    assert command == expected
    assert serializer.to_bytes(command) == data
