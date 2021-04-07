from .components import *

from tools import Mock

import pytest


@pytest.fixture
def client():
    yield Mock()


@pytest.fixture
def node(node_factory):
    node = node_factory.create_node(basic=0x04)
    node.add_to_network(123, 2)
    yield node


@pytest.fixture
def channel(node):
    main_channel = node.add_channel(generic=0x10, specific=0x01)
    main_channel.send_command = Mock()
    yield main_channel
