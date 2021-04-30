from network.application import Node

from tools import Mock

import pytest


@pytest.fixture(scope='session')
def node_info():
    yield {
        'channels': [
            {
                'generic': 0x10,
                'specific': 0x01,
                'associationGroups': [
                    {
                        'name': "Lifeline",
                        'profile': (0x00, 0x01),
                        'commands': [
                            (0x25, 0x03)
                        ]
                    }
                ],
                'commandClasses': [
                    {
                        'class_id': 0x72,  # COMMAND_CLASS_MANUFACTURER_SPECIFIC
                        'version': 1,
                        'state': {
                            'manufacturerId': 1,
                            'productTypeId': 2,
                            'productId': 3
                        }
                    },
                    {
                        'class_id': 0x5E,  # COMMAND_CLASS_ZWAVEPLUS_INFO
                        'version': 2,
                        'state': {
                            'zwavePlusVersion': 2,
                            'roleType': 0x05,
                            'nodeType': 0x00,
                            'installerIconType': 0x0700,
                            'userIconType': 0x0701
                        }
                    },
                    {
                        'class_id': 0x86,  # COMMAND_CLASS_VERSION
                        'version': 1,
                        'state': {
                            'protocolLibraryType': 0x06,
                            'protocolVersion': (1, 0),
                            'applicationVersion': (1, 0)
                        }
                    },
                    {
                        'class_id': 0x25,  # COMMAND_CLASS_SWITCH_BINARY
                        'version': 1
                    },
                    {
                        'class_id': 0x20,  # COMMAND_CLASS_SWITCH_BASIC
                        'version': 1,
                        'state': {
                            'mapped_command_class': 'COMMAND_CLASS_SWITCH_BINARY'
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture(scope='session', autouse=True)
def disable_node_command_handling():
    Node.handle_command = Mock()


@pytest.fixture
def node(node_manager, client, node_info):
    node = node_manager.generate_new_node(node_info)
    client.send_message.reset_mock()
    yield node


@pytest.fixture
def included_node(node):
    node.add_to_network(0xC0000000, 2)
    yield node
