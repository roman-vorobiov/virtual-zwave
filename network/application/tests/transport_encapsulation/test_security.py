from ..fixtures import *

from ...utils import SecurityUtils

from network.application.command_classes.application import BinarySwitch1
from network.application.command_classes.management import ManufacturerSpecific1
from network.application.command_classes.management import ZWavePlusInfo2
from network.application.command_classes.transport_encapsulation import Security1

from tools import make_object

import pytest
import asyncio
import random
from typing import List


@pytest.fixture
def security_utils():
    yield SecurityUtils()


@pytest.fixture
def network_key():
    yield random.randbytes(16)


@pytest.fixture
def tx_nonce_history():
    return []


@pytest.fixture
def rx_nonce_history():
    return []


@pytest.fixture
def generate_nonce(rx_nonce_history):
    def inner():
        nonce = list(random.randbytes(8))
        rx_nonce_history.append(nonce)
        return nonce

    yield inner


@pytest.fixture
def get_last_nonce(tx_nonce_history):
    original = Security1.generate_nonce

    def mock(cls):
        nonce = original()
        tx_nonce_history.append(nonce)
        return nonce

    Security1.generate_nonce = mock

    yield lambda: tx_nonce_history[-1]


@pytest.fixture
def encrypt(command_class, command_class_serializer, security_utils):
    def inner(sender_nonce: List[int], receiver_nonce: List[int], sender: int, receiver: int, command_name: str, args):
        command = make_command(command_class.class_id, command_name, command_class.class_version, **args)
        command_data = command_class_serializer.to_bytes(command)

        # Todo: split long commands
        payload = make_object(sequenced=False, second=False, sequence_counter=0, command=command_data)
        payload_data = command_class_serializer.from_object('EncryptedPayload', payload)

        return security_utils.encrypt_and_sign(payload_data, sender_nonce, receiver_nonce,
                                               header=0x81, sender=sender, receiver=receiver)

    yield inner


@pytest.fixture
def rx_encrypted(rx, tx, generate_nonce, get_last_nonce, encrypt):
    def inner(command_name: str, **kwargs):
        rx('SECURITY_NONCE_GET')
        tx('SECURITY_NONCE_REPORT', nonce=get_last_nonce())

        nonce = generate_nonce()
        encrypted, tag = encrypt(nonce, get_last_nonce(), 1, 2, command_name, kwargs)
        rx('SECURITY_MESSAGE_ENCAPSULATION',
           initialization_vector=nonce,
           encrypted_payload=encrypted,
           receiver_nonce_id=0,
           message_authentication_code=tag)

    yield inner


@pytest.fixture
def tx_encrypted(rx, tx, generate_nonce, get_last_nonce, encrypt):
    async def inner(command_name: str, **kwargs):
        nonce = generate_nonce()

        # Todo
        await asyncio.sleep(0)
        tx('SECURITY_NONCE_GET')
        await asyncio.sleep(0)
        rx('SECURITY_NONCE_REPORT', nonce=nonce)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        await asyncio.sleep(0)

        encrypted, tag = encrypt(get_last_nonce(), nonce, 2, 1, command_name, kwargs)
        tx('SECURITY_MESSAGE_ENCAPSULATION',
           initialization_vector=get_last_nonce(),
           encrypted_payload=encrypted,
           receiver_nonce_id=0,
           message_authentication_code=tag)

    yield inner


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
def binary_switch(channel, manufacturer_specific):
    yield channel.add_command_class(BinarySwitch1)


@pytest.fixture
def command_class(channel, binary_switch):
    yield channel.add_command_class(Security1)


@pytest.mark.asyncio
async def test_bootstrap(rx, tx, rx_encrypted, tx_encrypted, node, security_utils, network_key):
    assert not node.secure

    rx('SECURITY_SCHEME_GET', supported_security_schemes=0)
    tx('SECURITY_SCHEME_REPORT', supported_security_schemes=0)

    rx_encrypted('NETWORK_KEY_SET', network_key=network_key)
    security_utils.set_network_key(network_key)
    await tx_encrypted('NETWORK_KEY_VERIFY')

    assert node.secure
