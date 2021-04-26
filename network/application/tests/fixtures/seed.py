from network.application import NodeBuilder

import pytest


@pytest.fixture(scope='class')
def node(node_factory):
    node = node_factory.create_node()
    node.add_to_network(123, 2)
    node.set_suc_node_id(1)
    yield node


@pytest.fixture(scope='class')
def channel(node):
    yield node.add_channel(generic=0x10, specific=0x01)


@pytest.fixture(scope='class', autouse=True)
def check_serialization(node, node_factory):
    yield

    serialized = node.to_json()
    copy = NodeBuilder(node_factory).from_json(serialized)
    assert copy.to_json() == serialized
