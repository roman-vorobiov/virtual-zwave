from .fixture import *

from network.application.command_classes import make_command

from network.core.network_event_handler import NetworkEventHandler

import pytest
import json


@pytest.fixture
def included_node(node, node_manager):
    node_manager.add_node(0xC0000000, 2, node)
    yield node


@pytest.fixture
def network_event_handler(node_manager):
    yield NetworkEventHandler(node_manager)


@pytest.fixture
def rx(network_event_handler):
    def inner(message_type: str, message: dict):
        network_event_handler.handle_message(json.dumps({
            'messageType': message_type,
            'message': {
                **message,
                'source': {'homeId': 0xC0000000, 'nodeId': 1}
            }
        }))

    yield inner


@pytest.fixture
def tx(network):
    def inner(message_type: str, message: dict):
        assert network.free_buffer() == [{
            'messageType': message_type,
            'message': {
                **message,
                'destination': {'homeId': 0xC0000000, 'nodeId': 1}
            }
        }]

    yield inner


def test_add_to_network(rx, tx, node_manager, node):
    assert node_manager.nodes == {0: {1: node}}

    rx('ADD_TO_NETWORK', {
        'destination': {'homeId': 0, 'nodeId': 1},
        'newNodeId': 2
    })
    assert node_manager.nodes == {0: {}, 0xC0000000: {2: node}}


def test_remove_from_network(rx, tx, node_manager, included_node):
    assert node_manager.nodes == {0: {}, 0xC0000000: {2: included_node}}

    rx('REMOVE_FROM_NETWORK', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
    })
    assert node_manager.nodes == {0: {1: included_node}, 0xC0000000: {}}


def test_assign_suc_return_route(rx, tx, included_node):
    rx('ASSIGN_SUC_RETURN_ROUTE', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2},
        'sucNodeId': 1
    })
    assert included_node.suc_node_id == 1


def test_request_node_info(rx, tx, included_node):
    rx('REQUEST_NODE_INFO', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
    })
    tx('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': 0xC0000000, 'nodeId': 2},
        'nodeInfo': {
            'basic': 4,
            'generic': 1,
            'specific': 1,
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
