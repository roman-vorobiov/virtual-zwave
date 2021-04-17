from ..fixtures import *

from network.application.command_classes.application import Basic1


class TestBasic1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(Basic1)

    def test_basic_get(self, rx, tx):
        rx('BASIC_GET')
        tx('BASIC_REPORT', value=0xFE)

    def test_basic_set(self, rx, tx, tx_client, node, command_class):
        rx('BASIC_SET', value=123)
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })
        assert command_class.value == 123

        rx('BASIC_GET')
        tx('BASIC_REPORT', value=123)
