from network.application import Node

from tools import Mock

import pytest


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


@pytest.fixture
def included_node(node, node_manager, client):
    node_manager.add_to_network(node, 0xC0000000, 2)
    client.send_message.reset_mock()
    yield node