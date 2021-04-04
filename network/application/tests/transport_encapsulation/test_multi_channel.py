from ..fixtures import *

from network.application import Channel

from network.application.command_classes.application import Basic1
from network.application.command_classes.management import ManufacturerSpecific1
from network.application.command_classes.management import Version1
from network.application.command_classes.management import ZWavePlusInfo2
from network.application.command_classes.transport_encapsulation import MultiChannel3

import pytest


def make_command_class(cls, channel: Channel, **kwargs):
    cc = cls(channel, **kwargs)
    channel.add_command_class(cc)
    return cc


@pytest.fixture
def channel2(make_channel, channel):
    yield make_channel(generic=3, specific=4)


@pytest.fixture
def channel3(make_channel, channel2):
    yield make_channel(generic=5, specific=6)


@pytest.fixture
def zwaveplus_info(channel):
    yield make_command_class(ZWavePlusInfo2, channel,
                             zwave_plus_version=1, role_type=2, node_type=3, installer_icon_type=4, user_icon_type=5)


@pytest.fixture
def manufacturer_specific(channel, zwaveplus_info):
    yield make_command_class(ManufacturerSpecific1, channel,
                             manufacturer_id=1, product_type_id=2, product_id=3)


@pytest.fixture
def version(channel, manufacturer_specific):
    yield make_command_class(Version1, channel,
                             protocol_library_type=0x06, protocol_version=(1, 2), application_version=(3, 4))


@pytest.fixture
def basic2(channel2):
    yield make_command_class(Basic1, channel2, value=10)


@pytest.fixture
def basic3(channel3):
    yield make_command_class(Basic1, channel3, value=20)


class TestMultiChannel1:
    @pytest.fixture
    def command_class(self, channel, version, basic2, basic3):
        yield MultiChannel3(channel)

    def test_endpoint_get(self, rx, tx):
        rx('MULTI_CHANNEL_END_POINT_GET')
        tx('MULTI_CHANNEL_END_POINT_REPORT', dynamic=False, identical=False, endpoints=3)

    def test_capability_get(self, rx, tx):
        rx('MULTI_CHANNEL_CAPABILITY_GET', endpoint=0)
        tx('MULTI_CHANNEL_CAPABILITY_REPORT',
           dynamic=False,
           endpoint=0,
           generic_device_class=0x10,
           specific_device_class=0x01,
           command_class_ids=[0x5E, 0x72, 0x86, 0x60])

        rx('MULTI_CHANNEL_CAPABILITY_GET', endpoint=1)
        tx('MULTI_CHANNEL_CAPABILITY_REPORT',
           dynamic=False,
           endpoint=1,
           generic_device_class=3,
           specific_device_class=4,
           command_class_ids=[])

    def test_endpoint_find_existent(self, rx, tx):
        rx('MULTI_CHANNEL_END_POINT_FIND', generic_device_class=3, specific_device_class=4)
        tx('MULTI_CHANNEL_END_POINT_FIND_REPORT',
           reports_to_follow=0,
           generic_device_class=3,
           specific_device_class=4,
           endpoints=[1])

    def test_endpoint_find_non_existent(self, rx, tx):
        rx('MULTI_CHANNEL_END_POINT_FIND', generic_device_class=1, specific_device_class=2)
        tx('MULTI_CHANNEL_END_POINT_FIND_REPORT',
           reports_to_follow=0,
           generic_device_class=1,
           specific_device_class=2,
           endpoints=[])

    def test_receive_encapsulated_command(self, rx, tx):
        rx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=0,
           bit_address=False,
           destination=1,
           command=[0x20, 0x02])
        tx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=1,
           bit_address=False,
           destination=0,
           command=[0x20, 0x03, 0x0A])

    def test_receive_encapsulated_command_mask(self, rx, tx):
        rx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=0,
           bit_address=True,
           destination=0b00000110,
           command=[0x20, 0x02])
        tx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=1,
           bit_address=False,
           destination=0,
           command=[0x20, 0x03, 0x0A])
        tx('MULTI_CHANNEL_CMD_ENCAP',
           source_endpoint=2,
           bit_address=False,
           destination=0,
           command=[0x20, 0x03, 0x14])
