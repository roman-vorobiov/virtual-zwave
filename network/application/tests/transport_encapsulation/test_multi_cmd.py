from ..fixtures import *

from network.application.command_classes.management import ManufacturerSpecific1
from network.application.command_classes.management import ZWavePlusInfo2
from network.application.command_classes.transport_encapsulation import MultiCmd1

from tools import make_object

import pytest


@pytest.fixture
def zwaveplus_info(channel):
    yield channel.add_command_class(ZWavePlusInfo2,
                                    zwave_plus_version=1,
                                    role_type=2,
                                    node_type=3,
                                    installer_icon_type=4,
                                    user_icon_type=5)


@pytest.fixture
def manufacturer_specific(channel, zwaveplus_info):
    yield channel.add_command_class(ManufacturerSpecific1,
                                    manufacturer_id=1, product_type_id=2, product_id=3)


@pytest.fixture
def command_class(channel, manufacturer_specific):
    yield channel.add_command_class(MultiCmd1)


def test_receive_encapsulated_command(rx, tx):
    rx('MULTI_CMD_ENCAP', commands=[
        make_object(command=[0x72, 0x04]),
        make_object(command=[0x5E, 0x01])
    ])
    tx('MULTI_CMD_ENCAP', commands=[
        make_object(command=[0x72, 0x05, 0x00, 0x01, 0x00, 0x02, 0x00, 0x03]),
        make_object(command=[0x5E, 0x02, 0x01, 0x02, 0x03, 0x00, 0x04, 0x00, 0x05])
    ])
