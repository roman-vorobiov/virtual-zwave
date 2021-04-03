from .components import *

from controller.protocol import make_packet

import pytest
import json


@pytest.fixture
def rx(command_handler, requests_from_host_serializer):
    def inner(name: str, **kwargs):
        cmd = make_packet(name, **kwargs)
        command_handler.process_packet(requests_from_host_serializer.to_bytes(cmd))

    yield inner


@pytest.fixture
def tx_req(request_manager):
    async def inner(name: str, **kwargs):
        await request_manager.send_request.wait_until_called(timeout=2)
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
def tx_network(network):
    def inner(message_type: str, message: dict):
        assert network.free_buffer() == [{
            'messageType': message_type,
            'message': {
                'source': {'homeId': 0xC0000000, 'nodeId': 1},
                **message
            }
        }]

    yield inner


@pytest.fixture(autouse=True)
def check_communication(controller, request_manager, network):
    yield
    request_manager.send_request.assert_not_called()
    request_manager.send_response.assert_not_called()

    assert controller.free_buffer() == []

    assert network.free_buffer() == []
