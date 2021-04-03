from network.application import Node, Channel

from network.application.command_classes.application import Basic1
from network.application.command_classes.management import ManufacturerSpecific1
from network.application.command_classes.management import Version1
from network.application.command_classes.management import ZWavePlusInfo2
from network.application.command_classes.transport_encapsulation import MultiChannel3

from common import make_command

from tools import Mock

import pytest


@pytest.fixture
def node():
    node = Node(Mock(), basic=0x04)

    node.send_command = Mock()

    node.add_to_network(123, 2)

    yield node


@pytest.fixture
def tx(node, command_class):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, command_class.class_version, **kwargs)
        node.send_command.assert_called_first_with(1, command)
        node.send_command.pop_first_call()

    yield inner


@pytest.fixture
def rx(node, command_class):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, command_class.class_version, **kwargs)
        node.handle_command(1, command)

    yield inner


@pytest.fixture(autouse=True)
def check_communication(node):
    yield
    node.send_command.assert_not_called()


def make_channel(node: Node, generic: int, specific: int):
    channel = Channel(node, generic=generic, specific=specific)
    node.add_channel(channel)
    return channel


@pytest.fixture
def channel1(node):
    yield make_channel(node, generic=1, specific=2)


@pytest.fixture
def channel2(node, channel1):
    yield make_channel(node, generic=3, specific=4)


@pytest.fixture
def channel3(node, channel1):
    yield make_channel(node, generic=5, specific=6)


def make_command_class(cls, channel: Channel, **kwargs):
    cc = cls(channel, **kwargs)
    channel.add_command_class(cc)
    return cc


@pytest.fixture
def zwaveplus_info(channel1):
    yield make_command_class(ZWavePlusInfo2, channel1,
                             zwave_plus_version=1, role_type=2, node_type=3, installer_icon_type=4, user_icon_type=5)


@pytest.fixture
def manufacturer_specific(channel1, zwaveplus_info):
    yield make_command_class(ManufacturerSpecific1, channel1,
                             manufacturer_id=1, product_type_id=2, product_id=3)


@pytest.fixture
def version(channel1, manufacturer_specific):
    yield make_command_class(Version1, channel1,
                             protocol_library_type=0x06, protocol_version=(1, 2), application_version=(3, 4))


@pytest.fixture
def basic2(channel2):
    yield make_command_class(Basic1, channel2)


@pytest.fixture
def basic3(channel3):
    yield make_command_class(Basic1, channel3)


class TestMultiChannel1:
    @pytest.fixture
    def command_class(self, channel1, version, basic2, basic3):
        yield make_command_class(MultiChannel3, channel1)

    def test_endpoint_get(self, rx, tx):
        rx('MULTI_CHANNEL_END_POINT_GET')
        tx('MULTI_CHANNEL_END_POINT_REPORT', dynamic=False, identical=False, endpoints=3)

    def test_capability_get(self, rx, tx):
        rx('MULTI_CHANNEL_CAPABILITY_GET', endpoint=0)
        tx('MULTI_CHANNEL_CAPABILITY_REPORT',
           dynamic=False,
           endpoint=0,
           generic_device_class=1,
           specific_device_class=2,
           command_class_ids=[0x5E, 0x72, 0x86, 0x60])

        rx('MULTI_CHANNEL_CAPABILITY_GET', endpoint=1)
        tx('MULTI_CHANNEL_CAPABILITY_REPORT',
           dynamic=False,
           endpoint=1,
           generic_device_class=3,
           specific_device_class=4,
           command_class_ids=[])

    def test_endpoint_find(self, rx, tx):
        rx('MULTI_CHANNEL_END_POINT_FIND', generic_device_class=1, specific_device_class=2)
        tx('MULTI_CHANNEL_END_POINT_FIND_REPORT',
           reports_to_follow=0,
           generic_device_class=1,
           specific_device_class=2,
           endpoints=[0])

        rx('MULTI_CHANNEL_END_POINT_FIND', generic_device_class=3, specific_device_class=4)
        tx('MULTI_CHANNEL_END_POINT_FIND_REPORT',
           reports_to_follow=0,
           generic_device_class=3,
           specific_device_class=4,
           endpoints=[1])

    def test_receive_encapsulated_command(self, rx, tx):
        rx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=0,
           bit_address=False,
           destination=1,
           command=make_command(Basic1.class_id, 'BASIC_GET'))
        tx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=1,
           bit_address=False,
           destination=0,
           command=make_command(Basic1.class_id, 'BASIC_REPORT', value=0xFE))

    def test_receive_encapsulated_command_mask(self, rx, tx):
        rx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=0,
           bit_address=True,
           destination=0b00000110,
           command=make_command(Basic1.class_id, 'BASIC_GET'))
        tx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=1,
           bit_address=False,
           destination=0,
           command=make_command(Basic1.class_id, 'BASIC_REPORT', value=0xFE))
        tx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=2,
           bit_address=False,
           destination=0,
           command=make_command(Basic1.class_id, 'BASIC_REPORT', value=0xFE))
