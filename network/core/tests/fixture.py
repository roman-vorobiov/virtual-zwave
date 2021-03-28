from network.core.node_manager import NodeManager

from common.tests import FakeRemoteInterface

from tools import Mock

import pytest


@pytest.fixture
def controller():
    yield FakeRemoteInterface()


@pytest.fixture
def node_manager(controller):
    yield NodeManager(controller, Mock())


@pytest.fixture(autouse=True)
def node(node_manager):
    node = node_manager.generate_new_node()
    node.handle_command = Mock()
    yield node


@pytest.fixture(autouse=True)
def check_communication(controller):
    yield
    assert controller.free_buffer() == []
