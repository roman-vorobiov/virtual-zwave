from .fake_device import FakeDevice

from zwave.core.frame_handler import FrameHandler
from zwave.core.host import Host

from zwave.protocol import Packet
from zwave.protocol.serialization import PacketSerializer

from tools import load_yaml

import pytest
from unittest.mock import Mock


@pytest.fixture
def device():
    yield FakeDevice()


@pytest.fixture
def frame_serializer():
    yield PacketSerializer(load_yaml("zwave/protocol/frames/frames.yaml"))


@pytest.fixture
def host(frame_serializer, device):
    yield Host(frame_serializer, device)


@pytest.fixture
def frame_handler(frame_serializer, host):
    yield FrameHandler(frame_serializer, host, Mock())


@pytest.fixture
def push_rx(frame_handler, frame_serializer):
    yield lambda packet: frame_handler.process_packet(frame_serializer.to_bytes(packet))


@pytest.fixture
def check_tx(device, frame_serializer):
    def inner(packets):
        assert device.free_buffer() == [frame_serializer.to_bytes(packet) for packet in packets]

    yield inner


def test_ack_frame(push_rx, check_tx):
    push_rx(Packet('ACK'))
    check_tx([])


def test_nak_frame(push_rx, check_tx):
    push_rx(Packet('NAK'))
    check_tx([])


def test_can_frame(push_rx, check_tx):
    push_rx(Packet('CAN'))
    check_tx([])


def test_valid_data_frame(push_rx, check_tx):
    push_rx(Packet('Data', type=0x00, command=[], checksum=0xFD))
    check_tx([
        Packet('ACK')
    ])


def test_invalid_data_frame(push_rx, check_tx):
    push_rx(Packet('Data', type=0x00, command=[], checksum=0x00))
    check_tx([
        Packet('NAK')
    ])
