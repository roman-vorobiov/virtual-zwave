from .fixtures import *

from network.core.command_handler import CommandHandler

import humps
import pytest
import json


@pytest.fixture
def command_handler(client, node_manager):
    yield CommandHandler(client, node_manager)


@pytest.fixture
def rx_client(command_handler):
    def inner(message_type: str, message: dict):
        command_handler.handle_command(json.dumps({
            'messageType': message_type,
            'message': message
        }))

    yield inner


def test_get_nodes(rx_client, tx_client, included_node):
    rx_client('GET_NODES', {})
    tx_client('NODES_LIST', {
        'nodes': [humps.camelize(included_node.to_dict())]
    })


def test_send_nif(rx_client, tx_client, tx_controller, node):
    rx_client('SEND_NIF', {
        'id': node.id
    })
    tx_controller('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': node.home_id, 'nodeId': node.node_id},
        'nodeInfo': node.get_node_info().to_json()
    })


def test_create_node(rx_client, tx_client, tx_controller, nodes, node_info):
    assert len(nodes.all()) == 0

    rx_client('CREATE_NODE', {
        'node': node_info
    })
    assert len(nodes.all()) == 1
    tx_client('NODE_UPDATED', {
        'node': humps.camelize(nodes.all()[0])
    })


def test_reset(rx_client, tx_client, tx_controller, nodes, node):
    assert len(nodes.all()) == 1

    rx_client('RESET', {})
    tx_client('NODES_LIST', {
        'nodes': []
    })
    assert len(nodes.all()) == 0
