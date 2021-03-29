from .fixtures import *

from controller.core.command_handler import CommandHandler

from controller.protocol import make_packet
from controller.protocol.commands.send_data import TransmitStatus
from controller.protocol.commands.add_node_to_network import AddNodeMode, AddNodeStatus
from controller.protocol.commands.remove_node_from_network import RemoveNodeMode, RemoveNodeStatus

from tools import make_object

import pytest


@pytest.fixture
def command_handler(requests_from_host_serializer, request_manager, storage, library, network_controller):
    yield CommandHandler(requests_from_host_serializer, request_manager, storage, library, network_controller)


@pytest.fixture
def rx(command_handler, requests_from_host_serializer):
    def inner(name: str, **kwargs):
        cmd = make_packet(name, **kwargs)
        command_handler.process_packet(requests_from_host_serializer.to_bytes(cmd))

    yield inner


@pytest.fixture
def tx_req(request_manager):
    async def inner(name: str, **kwargs):
        await request_manager.send_request.wait_until_called(timeout=1)
        request_manager.send_request.assert_called_first_with(name, **kwargs)
        request_manager.send_request.pop_first_call()

    yield inner


@pytest.fixture
def tx_res(request_manager, command_handler, responses_to_host_serializer):
    def inner(name: str, **kwargs):
        request_manager.send_response.assert_called_first_with(name, **kwargs)
        request_manager.send_response.pop_first_call()

    yield inner


@pytest.fixture
def tx_network(network):
    def inner(message_type: str, message):
        assert network.free_buffer() == [{
            'messageType': message_type,
            'message': {
                'source': {'homeId': 0xC0000000, 'nodeId': 1},
                **message
            }
        }]

    yield inner


def test_application_node_information(rx, tx_req, tx_res):
    rx('APPLICATION_NODE_INFORMATION', device_options=0, generic=0, specific=0, command_class_ids=[])


def test_memory_get_id(rx, tx_req, tx_res):
    rx('MEMORY_GET_ID')
    tx_res('MEMORY_GET_ID', home_id=0xC0000000, node_id=1)


def test_version(rx, tx_req, tx_res):
    rx('VERSION')
    tx_res('VERSION', buffer="Z-Wave 4.05", library_type=0x01)


def test_set_listen_before_talk_threshold(rx, tx_req, tx_res):
    rx('SET_LISTEN_BEFORE_TALK_THRESHOLD', channel=0, threshold=0)
    tx_res('SET_LISTEN_BEFORE_TALK_THRESHOLD', result=True)


def test_get_suc_node_id(rx, tx_req, tx_res):
    rx('GET_SUC_NODE_ID')
    tx_res('GET_SUC_NODE_ID', node_id=1)


def test_set_suc_node_id_with_own_id(rx, tx_req, tx_res):
    rx('SET_SUC_NODE_ID', node_id=1, suc_state=0, tx_option=0, capabilities=0, function_id=0)
    tx_res('SET_SUC_NODE_ID', result=True)


def test_set_suc_node_id_with_foreign_id(rx, tx_req, tx_res):
    rx('SET_SUC_NODE_ID', node_id=2, suc_state=0, tx_option=0, capabilities=0, function_id=0)
    tx_res('SET_SUC_NODE_ID', result=False)


@pytest.mark.asyncio
async def test_add_node_to_network_no_node(rx, tx_req, tx_res, tx_network):
    rx('ADD_NODE_TO_NETWORK', mode=AddNodeMode.ANY, options=0, function_id=0)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.LEARN_READY, source=0, node_info=None)
    tx_network('ADD_NODE_STARTED', {})

    rx('ADD_NODE_TO_NETWORK', mode=AddNodeMode.STOP, options=0, function_id=0)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.DONE, source=0, node_info=None)


@pytest.mark.asyncio
async def test_add_node_to_network_with_node(rx, tx_req, tx_res, tx_network, network_controller):
    node_info = make_object(basic=1, generic=2, specific=3, command_class_ids=[4, 5, 6])

    rx('ADD_NODE_TO_NETWORK', mode=AddNodeMode.ANY, options=0, function_id=0)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.LEARN_READY, source=0, node_info=None)
    tx_network('ADD_NODE_STARTED', {})

    network_controller.on_node_information_frame(0, 1, node_info)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.NODE_FOUND, source=0, node_info=None)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.ADDING_SLAVE, source=2, node_info=node_info)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.PROTOCOL_DONE, source=2, node_info=None)
    tx_network('ADD_TO_NETWORK', {
        'destination': {
            'homeId': 0,
            'nodeId': 1
        },
        'newNodeId': 2
    })

    rx('ADD_NODE_TO_NETWORK', mode=AddNodeMode.STOP, options=0, function_id=0)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.DONE, source=2, node_info=None)


@pytest.mark.asyncio
async def test_add_node_to_network_stop(rx, tx_req, tx_res):
    rx('ADD_NODE_TO_NETWORK', mode=AddNodeMode.STOP, options=0, function_id=0)
    await tx_req('ADD_NODE_TO_NETWORK', function_id=0, status=AddNodeStatus.DONE, source=0, node_info=None)


@pytest.mark.asyncio
async def test_add_node_to_network_smart_start(rx, tx_req, tx_res):
    rx('ADD_NODE_TO_NETWORK', mode=AddNodeMode.SMART_START, options=0, function_id=0)


@pytest.mark.asyncio
async def test_remove_node_from_network_no_node(rx, tx_req, tx_res, tx_network):
    rx('REMOVE_NODE_FROM_NETWORK', mode=RemoveNodeMode.ANY, options=0, function_id=0)
    await tx_req('REMOVE_NODE_FROM_NETWORK', function_id=0, status=RemoveNodeStatus.LEARN_READY, source=0, node_info=None)
    tx_network('REMOVE_NODE_STARTED', {})

    rx('REMOVE_NODE_FROM_NETWORK', mode=RemoveNodeMode.STOP, options=0, function_id=0)


@pytest.mark.asyncio
async def test_remove_node_from_network_with_node(rx, tx_req, tx_res, tx_network, network_controller):
    node_info = make_object(basic=1, generic=2, specific=3, command_class_ids=[4, 5, 6])
    network_controller.nodes[2] = node_info

    rx('REMOVE_NODE_FROM_NETWORK', mode=RemoveNodeMode.ANY, options=0, function_id=0)
    await tx_req('REMOVE_NODE_FROM_NETWORK', function_id=0, status=RemoveNodeStatus.LEARN_READY, source=0, node_info=None)
    tx_network('REMOVE_NODE_STARTED', {})

    network_controller.on_node_information_frame(network_controller.home_id, 2, node_info)
    await tx_req('REMOVE_NODE_FROM_NETWORK', function_id=0, status=RemoveNodeStatus.NODE_FOUND, source=0, node_info=None)
    await tx_req('REMOVE_NODE_FROM_NETWORK', function_id=0, status=RemoveNodeStatus.REMOVING_SLAVE, source=2, node_info=node_info)
    await tx_req('REMOVE_NODE_FROM_NETWORK', function_id=0, status=RemoveNodeStatus.DONE, source=2, node_info=node_info)
    tx_network('REMOVE_FROM_NETWORK', {
        'destination': {
            'homeId': 0xC0000000,
            'nodeId': 2
        }
    })

    rx('REMOVE_NODE_FROM_NETWORK', mode=RemoveNodeMode.STOP, options=0, function_id=0)


@pytest.mark.asyncio
async def test_remove_node_from_network_stop(rx, tx_req, tx_res):
    rx('REMOVE_NODE_FROM_NETWORK', mode=RemoveNodeMode.STOP, options=0, function_id=0)


def test_get_node_protocol_info_no_node(rx, tx_req, tx_res, network):
    rx('GET_NODE_PROTOCOL_INFO', node_id=0)


def test_get_node_protocol_info_with_node(rx, tx_req, tx_res, network_controller):
    node_info = make_object(basic=1, generic=2, specific=3, command_class_ids=[4, 5, 6])
    network_controller.nodes[2] = node_info

    rx('GET_NODE_PROTOCOL_INFO', node_id=2)
    tx_res('GET_NODE_PROTOCOL_INFO', basic=1, generic=2, specific=3)


def test_request_node_info(rx, tx_req, tx_res, tx_network):
    rx('REQUEST_NODE_INFO', node_id=2)
    tx_res('REQUEST_NODE_INFO', result=True)
    tx_network('REQUEST_NODE_INFO', {
        'destination': {
            'homeId': 0xC0000000,
            'nodeId': 2
        }
    })


@pytest.mark.asyncio
async def test_send_data(rx, tx_req, tx_res, tx_network):
    rx('SEND_DATA', node_id=2, data=[0x20, 0x01, 0x10], tx_options=0, function_id=123)
    tx_res('SEND_DATA', result=True)
    await tx_req('SEND_DATA', function_id=123, tx_status=TransmitStatus.OK)
    tx_network('APPLICATION_COMMAND', {
        'destination': {
            'homeId': 0xC0000000,
            'nodeId': 2
        },
        'classId': 0x20,
        'command': 'BASIC_SET',
        'args': {
            'value': 0x10
        }
    })


@pytest.mark.asyncio
async def test_assign_suc_return_route(rx, tx_req, tx_res, tx_network):
    rx('ASSIGN_SUC_RETURN_ROUTE', node_id=2, function_id=123)
    tx_res('ASSIGN_SUC_RETURN_ROUTE', result=True)
    await tx_req('ASSIGN_SUC_RETURN_ROUTE', function_id=123, status=TransmitStatus.OK)
    tx_network('ASSIGN_SUC_RETURN_ROUTE', {
        'destination': {
            'homeId': 0xC0000000,
            'nodeId': 2
        },
        'sucNodeId': 1
    })


@pytest.mark.asyncio
async def test_set_default(rx, tx_req, tx_res):
    rx('SET_DEFAULT', function_id=123)
    await tx_req('SET_DEFAULT', function_id=123)


def test_nvm_get_value_unknown(rx, tx_req, tx_res):
    rx('NVR_GET_VALUE', offset=0, length=3)
    tx_res('NVR_GET_VALUE', data=[0xFF, 0xFF, 0xFF])


def test_nvm_get_value_known(rx, tx_req, tx_res):
    rx('NVR_GET_VALUE', offset=0x23, length=2)
    tx_res('NVR_GET_VALUE', data=[0x92, 0x9F])