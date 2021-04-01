from .in_memory_repository_provider import InMemoryRepositoryProvider

from network.core.node_manager import NodeManager
from network.application import Node, NodeFactory

from common.tests import FakeRemoteInterface

from tools import Mock

import pytest


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
def repository_provider(node_factory):
    yield InMemoryRepositoryProvider(node_factory)


@pytest.fixture
def nodes(repository_provider):
    yield repository_provider.get_nodes()


@pytest.fixture
def node_manager(client, node_factory, nodes):
    yield NodeManager(client, node_factory, nodes)


@pytest.fixture(autouse=True)
def node(node_manager, client):
    node = node_manager.generate_new_node()
    client.send_message.reset_mock()
    Node.handle_command = Mock()
    yield node


@pytest.fixture(autouse=True)
def check_communication(controller, client):
    yield
    assert controller.free_buffer() == []
    client.send_message.assert_not_called()
