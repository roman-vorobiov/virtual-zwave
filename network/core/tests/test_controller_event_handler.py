from .fixtures import *

from network.core.controller_event_handler import ControllerEventHandler

import json
import pytest


@pytest.fixture
def controller_event_handler(node_manager):
    yield ControllerEventHandler(node_manager)


@pytest.fixture
def rx_controller(controller_event_handler):
    def inner(message_type: str, message: dict):
        controller_event_handler.handle_message(json.dumps({
            'messageType': message_type,
            'message': {
                **message,
                'source': {'homeId': 0xC0000000, 'nodeId': 1}
            }
        }))

    yield inner


@pytest.fixture
def tx_client_node_updated_broadcast(nodes, tx_client):
    def inner(home_id: int, node_id: int):
        tx_client('NODE_UPDATED', {
            'node': nodes.find(home_id, node_id).to_json()
        })

    return inner


def test_add_to_network(rx_controller, tx_controller, tx_client_node_updated_broadcast, nodes, node):
    assert nodes.find(0, 1) == node

    rx_controller('ADD_TO_NETWORK', {
        'destination': {'homeId': 0, 'nodeId': 1},
        'newNodeId': 2
    })
    tx_client_node_updated_broadcast(0xC0000000, 2)
    assert nodes.find(0xC0000000, 2) == node


def test_remove_from_network(rx_controller, tx_controller, tx_client_node_updated_broadcast, nodes, included_node):
    assert nodes.find(0xC0000000, 2) == included_node

    rx_controller('REMOVE_FROM_NETWORK', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
    })
    tx_client_node_updated_broadcast(0, 1)
    assert nodes.find(0, 1) == included_node


def test_assign_suc_return_route(rx_controller, tx_controller, tx_client_node_updated_broadcast, nodes, included_node):
    assert nodes.find(0xC0000000, 2).suc_node_id is None

    rx_controller('ASSIGN_SUC_RETURN_ROUTE', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2},
        'sucNodeId': 1
    })
    tx_client_node_updated_broadcast(0xC0000000, 2)
    assert nodes.find(0xC0000000, 2).suc_node_id == 1


def test_request_node_info(rx_controller, tx_controller, included_node):
    rx_controller('REQUEST_NODE_INFO', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
    })
    tx_controller('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': 0xC0000000, 'nodeId': 2},
        'destination': {'homeId': 0xC0000000, 'nodeId': 1},
        'nodeInfo': {
            'generic': 0x10,
            'specific': 0x01,
            'commandClassIds': [0x72, 0x5E, 0x86]
        }
    })


def test_application_command(rx_controller, tx_controller, included_node):
    rx_controller('APPLICATION_COMMAND', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2},
        'command': [0x20, 0x01, 0x0A]
    })
    included_node.handle_command.assert_called_with(1, [0x20, 0x01, 0x0A])


def test_add_node_started(rx_controller, tx_controller):
    rx_controller('ADD_NODE_STARTED', {})


def test_remove_node_started(rx_controller, tx_controller):
    rx_controller('REMOVE_NODE_STARTED', {})
