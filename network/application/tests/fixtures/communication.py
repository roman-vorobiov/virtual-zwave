from .components import *
from .seed import *

from network.protocol import make_command

import pytest


@pytest.fixture
def rx(controller, node, command_class, command_class_serializer):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, command_class.class_version, **kwargs)
        data = command_class_serializer.to_bytes(command)

        node.handle_command(source_id=1, command=data)
        assert controller.pop() == {
            'messageType': 'ACK',
            'message': {
                'destination': {'homeId': 123, 'nodeId': 1},
                'source': {'homeId': 123, 'nodeId': 2}
            }
        }

    yield inner


@pytest.fixture
def tx(controller, command_class, command_class_serializer):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, command_class.class_version, **kwargs)
        data = command_class_serializer.to_bytes(command)

        assert controller.pop() == {
            'messageType': 'APPLICATION_COMMAND',
            'message': {
                'destination': {'homeId': 123, 'nodeId': 1},
                'source': {'homeId': 123, 'nodeId': 2},
                'command': data
            }
        }

    yield inner


@pytest.fixture
def tx_client(client):
    def inner(name: str, message):
        client.send_message.assert_called_first_with(name, message)
        client.send_message.pop_first_call()

    yield inner


@pytest.fixture(autouse=True)
def check_communication(controller, client):
    yield
    assert controller.free_buffer() == []
    client.send_message.assert_not_called()
