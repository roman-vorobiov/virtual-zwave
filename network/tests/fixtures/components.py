from .in_memory_repository_provider import InMemoryRepositoryProvider

from network.core.node_manager import NodeManager
from network.application import NodeFactory

from network.client import StateObserver
from network.protocol import CommandClassSerializer

from common.tests import FakeRemoteInterface

from tools import Mock, load_yaml

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


@pytest.fixture(scope='session')
def controller():
    yield FakeRemoteInterface()


@pytest.fixture(scope='session')
def client():
    yield Mock()


@pytest.fixture(scope='session')
def state_observer(client):
    yield StateObserver(client)


@pytest.fixture(scope='session')
def node_factory(controller, state_observer, command_class_serializer):
    yield NodeFactory(controller, state_observer, command_class_serializer)


@pytest.fixture
def repository_provider(node_factory):
    yield InMemoryRepositoryProvider(node_factory)


@pytest.fixture
def nodes(repository_provider):
    yield repository_provider.get_nodes()


@pytest.fixture
def node_manager(state_observer, node_factory, nodes):
    yield NodeManager(state_observer, node_factory, nodes)
