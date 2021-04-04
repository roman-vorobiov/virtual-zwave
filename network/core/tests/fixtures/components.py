from .in_memory_repository_provider import InMemoryRepositoryProvider

from network.core.node_manager import NodeManager
from network.application import NodeFactory, ChannelFactory

from controller.protocol.serialization import CommandClassSerializer

from common.tests import FakeRemoteInterface

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
def controller():
    yield FakeRemoteInterface()


@pytest.fixture
def client():
    yield Mock()


@pytest.fixture
def node_factory(controller):
    yield NodeFactory(controller)


@pytest.fixture
def channel_factory(command_class_serializer):
    yield ChannelFactory(command_class_serializer)


@pytest.fixture
def repository_provider(node_factory, channel_factory):
    yield InMemoryRepositoryProvider(node_factory, channel_factory)


@pytest.fixture
def nodes(repository_provider):
    yield repository_provider.get_nodes()


@pytest.fixture
def node_manager(client, node_factory, channel_factory, nodes):
    yield NodeManager(client, node_factory, channel_factory, nodes)
