from .components import *

from network.application import Node

from tools import Mock

import pytest


@pytest.fixture
def client():
    yield Mock()


@pytest.fixture
def node(client):
    node = Node(Mock(), client, basic=0x04)
    node.add_to_network(123, 2)
    yield node


@pytest.fixture
def make_channel(node, channel_factory):
    def inner(generic=0x10, specific=0x01):
        return channel_factory.create_channel(node, generic, specific)

    yield inner


@pytest.fixture
def channel(make_channel):
    main_channel = make_channel()
    main_channel.send_command = Mock()
    yield main_channel


@pytest.fixture(autouse=True)
def set_up_relations(channel, command_class):
    channel.add_command_class(command_class)
