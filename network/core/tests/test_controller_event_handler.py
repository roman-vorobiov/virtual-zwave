from .fixture import *

from network.core.controller_event_handler import ControllerEventHandler

from common import make_command

import pytest
import json


@pytest.fixture
def included_node(node, node_manager):
    node_manager.add_to_network(node, 0xC0000000, 2)
    yield node


@pytest.fixture
def controller_event_handler(node_manager):
    yield ControllerEventHandler(node_manager)


@pytest.fixture
def rx(controller_event_handler):
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
def tx(controller):
    def inner(message_type: str, message: dict):
        assert controller.free_buffer() == [{
            'messageType': message_type,
            'message': {
                **message,
                'destination': {'homeId': 0xC0000000, 'nodeId': 1}
            }
        }]

    yield inner


def test_add_to_network(rx, tx, nodes, node):
    assert nodes.find(0, 1) == node

    rx('ADD_TO_NETWORK', {
        'destination': {'homeId': 0, 'nodeId': 1},
        'newNodeId': 2
    })
    assert nodes.find(0xC0000000, 2) == node

    # Todo: test client notifications


def test_remove_from_network(rx, tx, nodes, included_node):
    assert nodes.find(0xC0000000, 2) == included_node

    rx('REMOVE_FROM_NETWORK', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
    })
    assert nodes.find(0, 1) == included_node


def test_assign_suc_return_route(rx, tx, nodes, included_node):
    assert nodes.find(0xC0000000, 2).suc_node_id is None

    rx('ASSIGN_SUC_RETURN_ROUTE', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2},
        'sucNodeId': 1
    })
    assert nodes.find(0xC0000000, 2).suc_node_id == 1


def test_request_node_info(rx, tx, included_node):
    rx('REQUEST_NODE_INFO', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
    })
    tx('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': 0xC0000000, 'nodeId': 2},
        'nodeInfo': {
            'basic': 0x04,
            'generic': 0x10,
            'specific': 0x01,
            'commandClassIds': [0x72, 0x5E]
        }
    })


def test_application_command(rx, tx, included_node):
    rx('APPLICATION_COMMAND', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2},
        'classId': 0x20,
        'command': 'BASIC_SET',
        'args': {
            'value': 123
        }
    })
    included_node.handle_command.assert_called_with(1, make_command(0x20, 'BASIC_SET', value=123))


def test_add_node_started(rx, tx):
    rx('ADD_NODE_STARTED', {})


def test_remove_node_started(rx, tx):
    rx('REMOVE_NODE_STARTED', {})
