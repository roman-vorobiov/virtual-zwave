from .fixtures import *

from zwave.core.command_handler import CommandHandler

from zwave.protocol import Packet

import pytest
from unittest.mock import Mock


@pytest.fixture
def command_handler(requests_from_host_serializer, request_manager, library, network):
    network.handle_add_node_to_network_command = Mock()
    yield CommandHandler(requests_from_host_serializer, request_manager, library, network)


@pytest.fixture
def rx(command_handler, requests_from_host_serializer):
    def inner(name: str, **kwargs):
        cmd = Packet(name, **kwargs)
        command_handler.process_packet(requests_from_host_serializer.to_bytes(cmd))

    yield inner


@pytest.fixture
def tx_req(request_manager, command_handler, requests_to_host_serializer):
    def inner(name: str, **kwargs):
        request_manager.send_request.assert_called_with(name, **kwargs)
        request_manager.send_request.reset_mock()

    yield inner


@pytest.fixture
def tx_res(request_manager, command_handler, responses_to_host_serializer):
    def inner(name: str, **kwargs):
        request_manager.send_response.assert_called_with(name, **kwargs)
        request_manager.send_response.reset_mock()

    yield inner


@pytest.fixture(autouse=True)
def check_communication(request_manager):
    yield
    request_manager.send_request.assert_not_called()
    request_manager.send_response.assert_not_called()


def test_application_node_information(rx, tx_req, tx_res):
    rx('APPLICATION_NODE_INFORMATION', device_options=0, generic=0, specific=0, command_class_ids=[])


def test_memory_get_id(rx, tx_req, tx_res):
    rx('MEMORY_GET_ID')
    tx_res('MEMORY_GET_ID', home_id=0, node_id=1)


def test_version(rx, tx_req, tx_res):
    rx('VERSION')
    tx_res('VERSION', buffer="Z-Wave 4.05", library_type=0x01)


def test_set_listen_before_talk_threshold(rx, tx_req, tx_res):
    rx('SET_LISTEN_BEFORE_TALK_THRESHOLD', channel=0, threshold=0)
    tx_res('SET_LISTEN_BEFORE_TALK_THRESHOLD', result=True)


def test_get_suc_node_id(rx, tx_req, tx_res):
    rx('GET_SUC_NODE_ID')
    tx_res('GET_SUC_NODE_ID', node_id=1)


def test_add_node_to_network(rx, tx_req, tx_res):
    rx('ADD_NODE_TO_NETWORK', mode=0, options=0, function_id=0)


def test_remove_node_from_network(rx, tx_req, tx_res):
    rx('REMOVE_NODE_FROM_NETWORK', mode=0, options=0, function_id=0)