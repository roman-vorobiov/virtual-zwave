from .fake_device import FakeDevice

from zwave.core.resources import Resources
from zwave.core.host import Host
from zwave.core.request_manager import RequestManager
from zwave.core.storage import Storage
from zwave.core.library import Library
from zwave.core.network import Network

from zwave.protocol.serialization import PacketSerializer

from tools import load_yaml

import pytest
from unittest import mock
from unittest.mock import Mock


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
def device():
    yield FakeDevice()


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
def network():
    with mock.patch('random.randint', lambda *args: 0):
        yield Network()
