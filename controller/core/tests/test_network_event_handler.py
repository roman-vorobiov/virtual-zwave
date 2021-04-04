from .fixtures.components import *
from .fixtures.communication import *

from controller.core.network_event_handler import NetworkEventHandler

from controller.protocol.commands.application_slave_update import UpdateStatus

from tools import make_object

import pytest


@pytest.fixture
def network_event_handler(network_controller, request_manager):
    yield NetworkEventHandler(network_controller, request_manager)


@pytest.mark.asyncio
async def test_application_command(rx_network, tx_network, tx_req):
    rx_network('APPLICATION_COMMAND', {
        'source': {'homeId': 0xC0000000, 'nodeId': 2},
        'command': [0x20, 0x01, 123]
    })
    tx_network('ACK', {
        'destination': {'homeId': 0xC0000000, 'nodeId': 2}
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
                 node_info=make_object(basic=0x04, generic=0x10, specific=0x01, command_class_ids=[0x72, 0x5E]))
