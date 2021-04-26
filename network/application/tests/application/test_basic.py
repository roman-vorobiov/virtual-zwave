from ..fixtures import *

from network.application.command_classes.application import Basic1


class TestBasic1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(Basic1)

    def test_basic_get(self, rx, tx):
        rx('BASIC_GET')
        tx('BASIC_REPORT', value=0xFE)

    def test_basic_set(self, rx, tx, assert_observed, command_class):
        rx('BASIC_SET', value=123)
        assert_observed(command_class)
        assert command_class.value == 123

        rx('BASIC_GET')
        tx('BASIC_REPORT', value=123)
