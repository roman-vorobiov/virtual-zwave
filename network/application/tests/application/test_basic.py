from ..fixtures import *

from network.application.command_classes.application import Basic1
from network.application.command_classes.application import BinarySwitch1


class TestBasic1:
    @pytest.fixture(scope='class', autouse=True)
    def binary_switch(self, channel):
        yield channel.add_command_class(BinarySwitch1)

    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(Basic1, mapping={
            'BASIC_GET': (BinarySwitch1.class_id, 'SWITCH_BINARY_GET', {}),
            'BASIC_SET': (BinarySwitch1.class_id, 'SWITCH_BINARY_SET', {'value': '$value'}),
            'BASIC_REPORT': (BinarySwitch1.class_id, 'SWITCH_BINARY_REPORT', {'value': '$value'})
        })

    def test_basic_get(self, rx, tx):
        rx('BASIC_GET')
        tx('BASIC_REPORT', value=0x00)

    def test_basic_set(self, rx, tx, assert_observed, binary_switch):
        assert binary_switch.value is False

        rx('BASIC_SET', value=0xFF)
        assert_observed(binary_switch)
        assert binary_switch.value is True
