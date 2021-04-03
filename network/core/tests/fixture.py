from .in_memory_repository_provider import InMemoryRepositoryProvider

from network.core.node_manager import NodeManager
from network.application import Node, NodeFactory

from common.tests import FakeRemoteInterface

from tools import Mock

import pytest


@pytest.fixture
def controller():
    yield FakeRemoteInterface()


@pytest.fixture
def client():
    yield Mock()


@pytest.fixture
def node_factory(controller):
    yield NodeFactory(controller)


@pytest.fixture
def repository_provider(node_factory):
    yield InMemoryRepositoryProvider(node_factory)


@pytest.fixture
def nodes(repository_provider):
    yield repository_provider.get_nodes()


@pytest.fixture
def node_manager(client, node_factory, nodes):
    yield NodeManager(client, node_factory, nodes)


@pytest.fixture
def node_info():
    yield {
        'basic': 0x04,
        'channels': [
            {
                'generic': 0x10,
                'specific': 0x01,
                'commandClasses': [
                    {
                        'id': 0x72,  # COMMAND_CLASS_MANUFACTURER_SPECIFIC
                        'version': 1,
                        'args': {
                            'manufacturerId': 1,
                            'productTypeId': 2,
                            'productId': 3
                        }
                    },
                    {
                        'id': 0x5E,  # COMMAND_CLASS_ZWAVEPLUS_INFO
                        'version': 2,
                        'args': {
                            'zwavePlusVersion': 2,
                            'roleType': 0x05,
                            'nodeType': 0x00,
                            'installerIconType': 0x0700,
                            'userIconType': 0x0701
                        }
                    },
                    {
                        'id': 0x86,  # COMMAND_CLASS_VERSION
                        'version': 1,
                        'args': {
                            'protocolLibraryType': 0x06,
                            'protocolVersion': (1, 0),
                            'applicationVersion': (1, 0)
                        }
                    },
                    {
                        'id': 0x20,  # COMMAND_CLASS_BASIC
                        'version': 1,
                        'args': {}
                    }
                ]
            }
        ]
    }


@pytest.fixture
def node(node_manager, client, node_info):
    node = node_manager.generate_new_node(node_info)
    client.send_message.reset_mock()
    Node.handle_command = Mock()
    yield node


@pytest.fixture(autouse=True)
def check_communication(controller, client):
    yield
    assert controller.free_buffer() == []
    client.send_message.assert_not_called()
