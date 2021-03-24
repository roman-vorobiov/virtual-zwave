from .fixtures import *

from zwave.core.network_event_handler import NetworkEventHandler

from zwave.protocol.commands.application_slave_update import UpdateStatus

from tools import Object, Mock

import pytest
import json


@pytest.fixture
def network_event_handler(network_controller, request_manager):
    yield NetworkEventHandler(Mock(), network_controller, request_manager)


@pytest.fixture
def rx_network(network_event_handler):
    def inner(message_type: str, message: dict):
        network_event_handler.process_message(json.dumps({
            'messageType': message_type,
            'message': {
                **message,
                'destination': {'homeId': 0xC0000000, 'nodeId': 1}
            }
        }))

    yield inner


@pytest.fixture
def tx_req(request_manager):
    async def inner(name: str, **kwargs):
        await request_manager.send_request.wait_until_called(timeout=1)
        request_manager.send_request.assert_called_first_with(name, **kwargs)
        request_manager.send_request.pop_first_call()

    yield inner


@pytest.mark.asyncio
async def test_application_command(rx_network, tx_req):
    rx_network('APPLICATION_COMMAND', {
        'source': {'homeId': 0xC0000000, 'nodeId': 2},
        'classId': 0x20,
        'command': 'BASIC_SET',
        'args': {
            'value': 123
        }
    })
    await tx_req('APPLICATION_COMMAND_HANDLER', rx_status=0, rx_type=0, source_node=2, command=[0x20, 0x01, 123])


@pytest.mark.asyncio
async def test_application_node_information(rx_network, tx_req):
    rx_network('APPLICATION_NODE_INFORMATION', {
        'source': {'homeId': 0xC0000000, 'nodeId': 2},
        'nodeInfo': {
            'basic': 0x04,
            'generic': 0x10,
            'specific': 0x01,
            'commandClassIds': [0x72, 0x5E]
        }
    })
    await tx_req('APPLICATION_SLAVE_UPDATE',
                 status=UpdateStatus.NODE_INFO_RECEIVED,
                 node_id=2,
                 node_info=Object(basic=0x04, generic=0x10, specific=0x01, command_class_ids=[0x72, 0x5E]))
