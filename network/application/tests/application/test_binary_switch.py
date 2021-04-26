from ..fixtures import *

from network.application.command_classes.application import BinarySwitch1


class TestBinarySwitch1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(BinarySwitch1)

    def test_switch_binary_get(self, rx, tx, command_class):
        assert not command_class.value

        rx('SWITCH_BINARY_GET')
        tx('SWITCH_BINARY_REPORT', value=0x00)

    def test_switch_binary_set(self, rx, tx, tx_client, node, command_class):
        assert not command_class.value

        rx('SWITCH_BINARY_SET', value=0XFF)
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })
        assert command_class.value
