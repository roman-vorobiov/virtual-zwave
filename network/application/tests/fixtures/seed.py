from network.tests.fixtures.components import *

import pytest


@pytest.fixture
def node(node_factory):
    node = node_factory.create_node()
    node.add_to_network(123, 2)
    yield node


@pytest.fixture
def channel(node):
    yield node.add_channel(generic=0x10, specific=0x01)
