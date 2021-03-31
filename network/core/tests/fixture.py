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
def node_factory(controller):
    yield NodeFactory(controller)


@pytest.fixture
def repository_provider(node_factory):
    yield InMemoryRepositoryProvider(node_factory)


@pytest.fixture
def nodes(repository_provider):
    yield repository_provider.get_nodes()


@pytest.fixture
def node_manager(node_factory, nodes):
    yield NodeManager(Mock(), node_factory, nodes)


@pytest.fixture(autouse=True)
def node(node_manager):
    node = node_manager.generate_new_node()
    Node.handle_command = Mock()
    yield node


@pytest.fixture(autouse=True)
def check_communication(controller):
    yield
    assert controller.free_buffer() == []
