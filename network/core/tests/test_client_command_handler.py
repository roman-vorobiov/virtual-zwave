from .fixtures import *

from network.core.command_handler import CommandHandler

import humps
import json
import pytest


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
        'nodes': [included_node.to_json()]
    })


def test_create_node(rx_client, tx_client, tx_controller, nodes, node_info):
    assert len(nodes.all()) == 0

    rx_client('CREATE_NODE', {
        'node': node_info
    })
    tx_client('NODE_ADDED', {
        'node': nodes.all()[0].to_json()
    })
    assert len(nodes.all()) == 1


def test_remove_node(rx_client, tx_client, tx_controller, nodes, node):
    assert len(nodes.all()) == 1

    rx_client('REMOVE_NODE', {
        'nodeId': node.id
    })
    tx_client('NODE_REMOVED', {
        'nodeId': node.id
    })
    assert len(nodes.all()) == 0


def test_reset(rx_client, tx_client, tx_controller, nodes, node):
    assert len(nodes.all()) == 1

    rx_client('RESET_NETWORK', {})
    tx_client('NODES_LIST', {
        'nodes': []
    })
    assert len(nodes.all()) == 0


def test_send_nif(rx_client, tx_client, tx_controller, node):
    rx_client('SEND_NIF', {
        'nodeId': node.id
    })
    tx_controller('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': node.home_id, 'nodeId': node.node_id},
        'nodeInfo': node.get_node_info().to_json()
    })


def test_update_node(rx_client, tx_client, tx_controller, node):
    command_class = node.root_channel.get_command_class(0x25)
    assert command_class.value is False

    rx_client('UPDATE_COMMAND_CLASS', {
        'nodeId': node.id,
        'channelId': node.root_channel.endpoint,
        'classId': 0x25,
        'state': {
            'value': True
        }
    })
    tx_client('COMMAND_CLASS_UPDATED', {
        'nodeId': node.id,
        'channelId': 0,
        'commandClass': humps.camelize(node.get_channel(0).command_classes[0x25].to_dict())
    })
    assert command_class.value is True


def test_reset_node(rx_client, tx_client, tx_controller, node):
    command_class = node.root_channel.get_command_class(0x25)
    command_class.value = True

    rx_client('RESET_NODE', {
        'nodeId': node.id
    })
    tx_client('NODE_RESET', {
        'node': node.to_json()
    })
    assert command_class.value is False
