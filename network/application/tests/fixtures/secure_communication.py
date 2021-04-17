from ..fixtures import *

from network.application.command_classes.transport_encapsulation import Security1
from network.protocol import make_command

from tools import Object, make_object

import pytest
import asyncio
import random
from typing import List


@pytest.fixture
def network_key():
    yield list(random.randbytes(16))


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


@pytest.fixture(autouse=True)
def mock_nonce_generation(tx_nonce_history):
    original = Security1.generate_nonce

    def mock(cls):
        nonce = original()
        tx_nonce_history.append(nonce)
        return nonce

    Security1.generate_nonce = mock
    yield
    Security1.generate_nonce = original


@pytest.fixture
def get_last_nonce(tx_nonce_history):
    yield lambda: tx_nonce_history[-1]


@pytest.fixture
def rx_nonce(generate_nonce, rx):
    async def inner(command_name: str):
        # Todo
        await asyncio.sleep(0)
        rx(command_name, nonce=generate_nonce())
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    yield inner


@pytest.fixture
def rx_payload(rx, command_class_serializer, security_utils, generate_nonce, get_last_nonce):
    def inner(command_name: str, payload: Object):
        header = {'SECURITY_MESSAGE_ENCAPSULATION': 0x81,
                  'SECURITY_MESSAGE_ENCAPSULATION_NONCE_GET': 0xC1}[command_name]

        payload_data = command_class_serializer.from_object('EncryptedPayload', payload)

        nonce = generate_nonce()

        encrypted, tag = security_utils.encrypt_and_sign(payload_data, nonce, get_last_nonce(),
                                                         header=header, sender=1, receiver=2)

        rx(command_name,
           initialization_vector=nonce,
           encrypted_payload=encrypted,
           receiver_nonce_id=get_last_nonce()[0],
           message_authentication_code=tag)

    yield inner


@pytest.fixture
def rx_encrypted(rx_encrypted_short, rx_encrypted_long, command_class_serializer):
    def inner(command_name: str, class_id=None, /, **kwargs):
        command = make_command(class_id or Security1.class_id, command_name, Security1.class_version, **kwargs)
        command_data = command_class_serializer.to_bytes(command)

        if len(command_data) <= 26:
            rx_encrypted_short(command_data)
        else:
            rx_encrypted_long(command_data)

    yield inner


@pytest.fixture
def rx_encrypted_short(rx, tx, get_last_nonce, rx_payload):
    def inner(command: List[int]):
        rx('SECURITY_NONCE_GET')
        tx('SECURITY_NONCE_REPORT', nonce=get_last_nonce())

        rx_payload('SECURITY_MESSAGE_ENCAPSULATION',
                   make_object(sequenced=False, second=False, sequence_counter=0, command=command))

    yield inner


@pytest.fixture
def rx_encrypted_long(rx, tx, get_last_nonce, rx_payload):
    def inner(command: List[int]):
        rx('SECURITY_NONCE_GET')
        tx('SECURITY_NONCE_REPORT', nonce=get_last_nonce())

        rx_payload('SECURITY_MESSAGE_ENCAPSULATION_NONCE_GET',
                   make_object(sequenced=True, second=False, sequence_counter=0, command=command[:26]))
        tx('SECURITY_NONCE_REPORT', nonce=get_last_nonce())

        rx_payload('SECURITY_MESSAGE_ENCAPSULATION',
                   make_object(sequenced=True, second=True, sequence_counter=0, command=command[26:]))

    yield inner


@pytest.fixture
def tx_payload(tx, command_class_serializer, security_utils, rx_nonce_history, get_last_nonce):
    def inner(command_name: str, payload: Object):
        header = {'SECURITY_MESSAGE_ENCAPSULATION': 0x81,
                  'SECURITY_MESSAGE_ENCAPSULATION_NONCE_GET': 0xC1}[command_name]

        payload_data = command_class_serializer.from_object('EncryptedPayload', payload)

        encrypted, tag = security_utils.encrypt_and_sign(payload_data, get_last_nonce(), rx_nonce_history[-1],
                                                         header=header, sender=2, receiver=1)

        tx(command_name,
           initialization_vector=get_last_nonce(),
           encrypted_payload=encrypted,
           receiver_nonce_id=rx_nonce_history[-1][0],
           message_authentication_code=tag)

    yield inner


@pytest.fixture
def tx_encrypted(tx_encrypted_short, tx_encrypted_long, command_class_serializer):
    async def inner(command_name: str, class_id=None, /, **kwargs):
        command = make_command(class_id or Security1.class_id, command_name, Security1.class_version, **kwargs)
        command_data = command_class_serializer.to_bytes(command)

        if len(command_data) <= 26:
            await tx_encrypted_short(command_data)
        else:
            await tx_encrypted_long(command_data)

    yield inner


@pytest.fixture
def tx_encrypted_short(tx, rx_nonce, tx_payload):
    async def inner(command: List[int]):
        await asyncio.sleep(0)

        tx('SECURITY_NONCE_GET')
        await rx_nonce('SECURITY_NONCE_REPORT')

        tx_payload('SECURITY_MESSAGE_ENCAPSULATION',
                   make_object(sequenced=False, second=False, sequence_counter=0, command=command))

    yield inner


@pytest.fixture
def tx_encrypted_long(tx, rx_nonce, tx_payload):
    async def inner(command: List[int]):
        await asyncio.sleep(0)

        tx('SECURITY_NONCE_GET')
        await rx_nonce('SECURITY_NONCE_REPORT')

        tx_payload('SECURITY_MESSAGE_ENCAPSULATION_NONCE_GET',
                   make_object(sequenced=True, second=False, sequence_counter=0, command=command[:26]))

        await rx_nonce('SECURITY_NONCE_REPORT')

        tx_payload('SECURITY_MESSAGE_ENCAPSULATION',
                   make_object(sequenced=True, second=True, sequence_counter=0, command=command[26:]))

    yield inner


@pytest.fixture
def bootstrap(rx, tx, rx_encrypted, tx_encrypted, node, security_utils, network_key):
    async def inner():
        assert not node.secure

        rx('SECURITY_SCHEME_GET', supported_security_schemes=0)
        tx('SECURITY_SCHEME_REPORT', supported_security_schemes=0)

        rx_encrypted('NETWORK_KEY_SET', network_key=network_key)
        security_utils.set_network_key(network_key)
        await tx_encrypted('NETWORK_KEY_VERIFY')

        assert node.secure

    yield inner

    node.add_to_network(home_id=123, node_id=2)
    node.set_suc_node_id(1)

    security_utils.reset()
