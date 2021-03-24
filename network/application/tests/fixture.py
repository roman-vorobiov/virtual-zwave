from network.application.node import Node
from network.application.command_classes import make_command

from zwave.protocol import Packet

from tools import Mock

import pytest


@pytest.fixture
def node():
    node = Node(Mock(), basic=0x04, generic=0x10, specific=0x01)

    node.send_command = Mock()

    node.add_to_network(123, 2)

    yield node


@pytest.fixture
def tx(node):
    def inner(name: str, **kwargs):
        command = Packet(name, **kwargs)
        node.send_command.assert_called_first_with(1, command)
        node.send_command.pop_first_call()

    yield inner


@pytest.fixture
def rx(node, command_class):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, **kwargs)
        node.handle_command(1, command)

    yield inner


@pytest.fixture(autouse=True)
def check_communication(node):
    yield
    node.send_command.assert_not_called()
