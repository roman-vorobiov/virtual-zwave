from .fixture import *

from network.core.command_handler import CommandHandler

import humps
import pytest
import json


@pytest.fixture
def included_node(node, node_manager, client):
    node_manager.add_to_network(node, 0xC0000000, 2)
    client.send_message.reset_mock()
    yield node


@pytest.fixture
def command_handler(client, node_manager):
    yield CommandHandler(client, node_manager)


@pytest.fixture
def rx(command_handler):
    def inner(message_type: str, message: dict):
        command_handler.handle_command(json.dumps({
            'messageType': message_type,
            'message': message
        }))

    yield inner


@pytest.fixture
def tx(client):
    def inner(message_type: str, message: dict):
        client.send_message.assert_called_first_with(message_type, message)
        client.send_message.pop_first_call()

    return inner


@pytest.fixture
def tx_controller(controller):
    def inner(message_type: str, message: dict):
        assert controller.free_buffer() == [{
            'messageType': message_type,
            'message': message
        }]

    yield inner


def test_get_nodes(rx, tx, included_node):
    rx('GET_NODES', {})
    tx('NODES_LIST', {
        'nodes': [humps.camelize(included_node.to_dict())]
    })


def test_send_nif(rx, tx, tx_controller, node):
    rx('SEND_NIF', {
        'id': node.id
    })
    tx_controller('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': node.home_id, 'nodeId': node.node_id},
        'nodeInfo': node.get_node_info().to_json()
    })


def test_create_node(rx, tx, tx_controller, nodes):
    assert len(nodes.all()) == 1

    rx('CREATE_NODE', {})
    tx('NODE_UPDATED', humps.camelize(nodes.all()[1]))
    assert len(nodes.all()) == 2


def test_reset(rx, tx, tx_controller, nodes):
    assert len(nodes.all()) == 1

    rx('RESET', {})
    tx('NODES_LIST', {
        'nodes': []
    })
    assert len(nodes.all()) == 0


