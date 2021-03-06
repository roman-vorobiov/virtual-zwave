from .fake_controller import FakeController
from .in_memory_repository_provider import InMemoryRepositoryProvider

from controller.core.host import Host
from controller.core.request_manager import RequestManager
from controller.core.storage import Storage
from controller.core.library import Library
from controller.core.network_controller import NetworkController

from controller.protocol import PacketSerializer

from common.tests import FakeRemoteInterface

from tools import Mock, Resources, load_yaml

import pytest
from unittest import mock


@pytest.fixture(scope='session')
def frame_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/frames/frames.yaml"))


@pytest.fixture(scope='session')
def requests_from_host_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/commands/requests_from_host.yaml"))


@pytest.fixture(scope='session')
def requests_to_host_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/commands/requests_to_host.yaml"))


@pytest.fixture(scope='session')
def responses_to_host_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/commands/responses_to_host.yaml"))


@pytest.fixture
def controller():
    yield FakeController()


@pytest.fixture
def network():
    yield FakeRemoteInterface()


@pytest.fixture
def repository_provider():
    yield InMemoryRepositoryProvider()


@pytest.fixture
def state(repository_provider):
    yield repository_provider.get_state()


@pytest.fixture
def node_info_repository(repository_provider):
    yield repository_provider.get_node_infos()


@pytest.fixture
def host(frame_serializer, controller):
    yield Host(frame_serializer, controller)


@pytest.fixture
def request_manager(requests_to_host_serializer, responses_to_host_serializer, host):
    obj = RequestManager(requests_to_host_serializer, responses_to_host_serializer, host)
    obj.send_response = Mock()
    obj.send_request = Mock()
    yield obj


@pytest.fixture(scope='session')
def config():
    yield Resources("controller/resources/config.yaml")


@pytest.fixture
def library(config):
    yield Library(config)


@pytest.fixture
def storage(config):
    yield Storage(config)


@pytest.fixture
def network_controller(state, node_info_repository, request_manager, network):
    with mock.patch('random.randint', lambda *args: 0xC0000000):
        yield NetworkController(state, node_info_repository, request_manager, network)
