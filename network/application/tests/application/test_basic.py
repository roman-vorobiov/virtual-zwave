from ..fixtures import *

from network.application.command_classes.application import Basic1


@pytest.fixture(autouse=True)
def command_class(channel):
    yield channel.add_command_class(Basic1)


def test_basic_get(rx, tx):
    rx('BASIC_GET')
    tx('BASIC_REPORT', value=0xFE)


def test_basic_set(rx, tx, tx_client, node, command_class):
    rx('BASIC_SET', value=123)
    tx_client('NODE_UPDATED', {
        'node': node.to_json()
    })
    assert command_class.value == 123

    rx('BASIC_GET')
    tx('BASIC_REPORT', value=123)
