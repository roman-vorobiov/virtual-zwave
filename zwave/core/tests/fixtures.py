from .fake_device import FakeDevice

from zwave.core.resources import Resources
from zwave.core.host import Host
from zwave.core.request_manager import RequestManager
from zwave.core.storage import Storage
from zwave.core.library import Library
from zwave.core.network_controller import NetworkController

from zwave.protocol.serialization import PacketSerializer, CommandClassSerializer

from common.tests import FakeNetwork

from tools import Mock, load_yaml

import pytest
from unittest import mock


@pytest.fixture
def frame_serializer():
    yield PacketSerializer(load_yaml("zwave/protocol/frames/frames.yaml"))


@pytest.fixture
def requests_from_host_serializer():
    yield PacketSerializer(load_yaml("zwave/protocol/commands/requests_from_host.yaml"))


@pytest.fixture
def requests_to_host_serializer():
    yield PacketSerializer(load_yaml("zwave/protocol/commands/requests_to_host.yaml"))


@pytest.fixture
def responses_to_host_serializer():
    yield PacketSerializer(load_yaml("zwave/protocol/commands/responses_to_host.yaml"))


@pytest.fixture
def command_class_serializer():
    schema_files = [
        "zwave/protocol/command_classes/management.yaml",
        "zwave/protocol/command_classes/application.yaml"
    ]

    data = {}
    for schema_file in schema_files:
        data.update(load_yaml(schema_file))

    yield CommandClassSerializer(data)


@pytest.fixture
def device():
    yield FakeDevice()


@pytest.fixture
def network():
    yield FakeNetwork()


@pytest.fixture
def host(frame_serializer, device):
    yield Host(frame_serializer, device)


@pytest.fixture
def request_manager(requests_to_host_serializer, responses_to_host_serializer, host):
    obj = RequestManager(requests_to_host_serializer, responses_to_host_serializer, host)
    obj.send_response = Mock()
    obj.send_request = Mock()
    yield obj


@pytest.fixture
def resources():
    yield Resources()


@pytest.fixture
def library(resources):
    yield Library(resources)


@pytest.fixture
def storage(resources):
    yield Storage(resources)


@pytest.fixture
def network_controller(network, command_class_serializer, request_manager):
    with mock.patch('random.randint', lambda *args: 0xC0000000):
        yield NetworkController(command_class_serializer, request_manager, network)


@pytest.fixture(autouse=True)
def check_communication(device, request_manager, network):
    yield
    request_manager.send_request.assert_not_called()
    request_manager.send_response.assert_not_called()

    assert device.free_buffer() == []

    assert network.free_buffer() == []
