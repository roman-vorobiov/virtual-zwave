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

    def test_switch_binary_set(self, rx, tx, assert_observed, command_class):
        assert not command_class.value

        rx('SWITCH_BINARY_SET', value=0XFF)
        assert_observed(command_class)
        assert command_class.value
