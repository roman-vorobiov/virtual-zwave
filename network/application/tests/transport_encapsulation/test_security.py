from ..fixtures import *

from network.application.command_classes import SecurityLevel
from network.application.command_classes.application import BinarySwitch1
from network.application.command_classes.management import ManufacturerSpecific1
from network.application.command_classes.management import ZWavePlusInfo2
from network.application.command_classes.management import Version1
from network.application.command_classes.transport_encapsulation import Security1
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
def version(channel, manufacturer_specific):
    yield channel.add_command_class(Version1, SecurityLevel.GRANTED,
                                    protocol_library_type=1, protocol_version=2, application_version=3)


@pytest.fixture
def binary_switch(channel, version):
    yield channel.add_command_class(BinarySwitch1, SecurityLevel.SUPPORTED)


@pytest.fixture
def multi_cmd(channel, binary_switch):
    yield channel.add_command_class(MultiCmd1)


@pytest.fixture
def command_class(channel, multi_cmd):
    yield channel.add_command_class(Security1)


@pytest.mark.asyncio
async def test_bootstrap(bootstrap):
    await bootstrap()


@pytest.mark.asyncio
async def test_nif(rx, rx_encrypted, tx_encrypted, bootstrap, node):
    # Check before bootstrap
    assert node.get_node_info().command_class_ids == [
        ZWavePlusInfo2.class_id,
        ManufacturerSpecific1.class_id,
        Version1.class_id,
        MultiCmd1.class_id,
        Security1.class_id
    ]

    await bootstrap()

    # Check after bootstrap
    assert node.get_node_info().command_class_ids == [
        ZWavePlusInfo2.class_id,
        ManufacturerSpecific1.class_id,
        MultiCmd1.class_id,
        Security1.class_id
    ]


@pytest.mark.asyncio
async def test_commands_supported_get(rx, rx_encrypted, tx_encrypted, bootstrap):
    # Check before bootstrap
    rx('SECURITY_COMMANDS_SUPPORTED_GET')

    await bootstrap()

    # Check after bootstrap unencrypted
    rx('SECURITY_COMMANDS_SUPPORTED_GET')

    # Check after bootstrap encrypted
    rx_encrypted('SECURITY_COMMANDS_SUPPORTED_GET')
    await tx_encrypted('SECURITY_COMMANDS_SUPPORTED_REPORT',
                       reports_to_follow=0,
                       command_class_ids=[Version1.class_id, BinarySwitch1.class_id])


@pytest.mark.asyncio
async def test_secure_command_class_highest_supported(rx, rx_encrypted, tx_encrypted, bootstrap):
    # Check before bootstrap
    rx('SWITCH_BINARY_GET', BinarySwitch1.class_id)

    await bootstrap()

    # Check after bootstrap unencrypted
    rx('SWITCH_BINARY_GET', BinarySwitch1.class_id)

    # Check after bootstrap encrypted
    rx_encrypted('SWITCH_BINARY_GET', BinarySwitch1.class_id)
    await tx_encrypted('SWITCH_BINARY_REPORT', BinarySwitch1.class_id, value=0xFE)


@pytest.mark.asyncio
async def test_secure_command_class_highest_granted(rx, tx, rx_encrypted, tx_encrypted, bootstrap):
    # Check before bootstrap
    rx('VERSION_COMMAND_CLASS_GET', Version1.class_id, class_id=Security1.class_id)
    tx('VERSION_COMMAND_CLASS_REPORT', Version1.class_id, class_id=Security1.class_id, version=1)

    await bootstrap()

    # Check after bootstrap unencrypted
    rx('VERSION_COMMAND_CLASS_GET', Version1.class_id, class_id=Security1.class_id)

    # Check after bootstrap encrypted
    rx_encrypted('VERSION_COMMAND_CLASS_GET', Version1.class_id, class_id=Security1.class_id)
    await tx_encrypted('VERSION_COMMAND_CLASS_REPORT', Version1.class_id, class_id=Security1.class_id, version=1)


@pytest.mark.asyncio
async def test_non_secure_command_class(rx, tx, rx_encrypted, tx_encrypted, bootstrap):
    # Check before bootstrap
    rx('MANUFACTURER_SPECIFIC_GET', ManufacturerSpecific1.class_id)
    tx('MANUFACTURER_SPECIFIC_REPORT', ManufacturerSpecific1.class_id,
       manufacturer_id=1, product_type_id=2, product_id=3)

    await bootstrap()

    # Check after bootstrap unencrypted
    rx('MANUFACTURER_SPECIFIC_GET', ManufacturerSpecific1.class_id)
    tx('MANUFACTURER_SPECIFIC_REPORT', ManufacturerSpecific1.class_id,
       manufacturer_id=1, product_type_id=2, product_id=3)

    # Check after bootstrap encrypted
    rx_encrypted('MANUFACTURER_SPECIFIC_GET', ManufacturerSpecific1.class_id)
    await tx_encrypted('MANUFACTURER_SPECIFIC_REPORT', ManufacturerSpecific1.class_id,
                       manufacturer_id=1, product_type_id=2, product_id=3)


@pytest.mark.asyncio
async def test_send_long_response(rx_encrypted, tx_encrypted, bootstrap):
    await bootstrap()

    rx_encrypted('MULTI_CMD_ENCAP', MultiCmd1.class_id,
                 commands=[make_object(command=[0x72, 0x04])] * 3)
    await tx_encrypted('MULTI_CMD_ENCAP', MultiCmd1.class_id,
                       commands=[make_object(command=[0x72, 0x05, 0x00, 0x01, 0x00, 0x02, 0x00, 0x03])] * 3)


@pytest.mark.asyncio
async def test_handle_long_command(rx_encrypted, tx_encrypted, bootstrap):
    await bootstrap()

    rx_encrypted('MULTI_CMD_ENCAP', Version1.class_id,
                 commands=[make_object(command=[0x86, 0x13, 0x98])] * 8)
    await tx_encrypted('MULTI_CMD_ENCAP', MultiCmd1.class_id,
                       commands=[make_object(command=[0x86, 0x14, 0x98, 0x01])] * 8)
