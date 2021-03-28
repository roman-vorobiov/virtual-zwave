from network.core.node_manager import NodeManager

from common.tests import FakeNetwork

from tools import Mock

import pytest


@pytest.fixture
def network():
    yield FakeNetwork()


@pytest.fixture
def node_manager(network):
    yield NodeManager(network, Mock())


@pytest.fixture(autouse=True)
def node(node_manager):
    node = node_manager.generate_new_node()
    node.handle_command = Mock()
    yield node


@pytest.fixture(autouse=True)
def check_communication(network):
    yield
    assert network.free_buffer() == []
