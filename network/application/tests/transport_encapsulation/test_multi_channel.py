from ..fixtures import *

from network.application.command_classes.application import Basic1
from network.application.command_classes.management import ManufacturerSpecific1
from network.application.command_classes.management import Version1
from network.application.command_classes.management import ZWavePlusInfo2
from network.application.command_classes.transport_encapsulation import MultiChannel3

import pytest


class TestMultiChannel1:
    @pytest.fixture(scope='class')
    def channel2(self, node, channel):
        yield node.add_channel(generic=3, specific=4)

    @pytest.fixture(scope='class')
    def channel3(self, node, channel2):
        yield node.add_channel(generic=5, specific=6)

    @pytest.fixture(scope='class')
    def zwaveplus_info(self, channel):
        yield channel.add_command_class(ZWavePlusInfo2,
                                        zwave_plus_version=1,
                                        role_type=2,
                                        node_type=3,
                                        installer_icon_type=4,
                                        user_icon_type=5)

    @pytest.fixture(scope='class')
    def manufacturer_specific(self, channel, zwaveplus_info):
        yield channel.add_command_class(ManufacturerSpecific1,
                                        manufacturer_id=1, product_type_id=2, product_id=3)

    @pytest.fixture(scope='class')
    def version(self, channel, manufacturer_specific):
        yield channel.add_command_class(Version1,
                                        protocol_library_type=0x06, protocol_version=(1, 2), application_version=(3, 4))

    @pytest.fixture(scope='class')
    def basic2(self, channel2):
        yield channel2.add_command_class(Basic1, value=10)

    @pytest.fixture(scope='class')
    def basic3(self, channel3):
        yield channel3.add_command_class(Basic1, value=20)

    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel, version, basic2, basic3):
        yield channel.add_command_class(MultiChannel3)

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
           command_class_ids=[0x5E, 0x72, 0x86])

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
