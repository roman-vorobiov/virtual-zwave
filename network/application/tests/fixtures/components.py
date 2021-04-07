from network.application import NodeFactory
from network.protocol import CommandClassSerializer

from tools import load_yaml, Mock

import pytest


@pytest.fixture(scope='session')
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
def controller():
    yield Mock()


@pytest.fixture
def client():
    yield Mock()


@pytest.fixture
def node_factory(controller, client, command_class_serializer):
    yield NodeFactory(controller, client, command_class_serializer)
