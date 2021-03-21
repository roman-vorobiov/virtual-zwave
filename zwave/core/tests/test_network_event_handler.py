from .fixtures import *

from network.application.command_classes import make_command

from zwave.core.network_event_handler import NetworkEventHandler

from tools import Mock, Object

import pytest
import json


@pytest.fixture
def network_event_handler(network_controller):
    network_controller.on_application_command = Mock()
    network_controller.on_node_information_frame = Mock()

    yield NetworkEventHandler(Mock(), network_controller)


def test_application_command(network_event_handler, network_controller):
    message = {
        'messageType': "APPLICATION_COMMAND",
        'message': {
            'sourceNodeId': 1,
            'destinationNodeId': 2,
            'classId': 0x20,
            'command': 'BASIC_SET',
            'args': {
                'value': 123
            }
        }
    }

    network_event_handler.process_message(json.dumps(message))

    command = make_command(0x20, 'BASIC_SET', value=123)
    network_controller.on_application_command.assert_called_with(1, command)


def test_application_node_information(network_event_handler, network_controller):
    message = {
        'messageType': 'APPLICATION_NODE_INFORMATION',
        'message': {
            'homeId': 1,
            'sourceNodeId': 2,
            'destinationNodeId': 3,
            'nodeInfo': {
                'basic': 4,
                'generic': 5,
                'specific': 6,
                'command_class_ids': [7, 8]
            }
        }
    }

    network_event_handler.process_message(json.dumps(message))

    node_info = Object(basic=4, generic=5, specific=6, command_class_ids=[7, 8])
    network_controller.on_node_information_frame.assert_called_with(2, node_info)
