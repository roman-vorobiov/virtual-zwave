from ..fixtures import *

from network.application.command_classes.application import BinarySwitch1


class TestBinarySwitch1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(BinarySwitch1)

    def test_switch_binary_get(self, rx, tx):
        rx('SWITCH_BINARY_GET')
        tx('SWITCH_BINARY_REPORT', value=0xFE)

    def test_switch_binary_set(self, rx, tx, tx_client, node, command_class):
        rx('SWITCH_BINARY_SET', value=123)
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })
        assert command_class.value == 123

        rx('SWITCH_BINARY_GET')
        tx('SWITCH_BINARY_REPORT', value=123)
