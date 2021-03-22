from .fixtures import *

from zwave.core.frame_handler import FrameHandler

from zwave.protocol import Packet
from zwave.protocol.frames.data import FrameType

from tools import Mock

import pytest


@pytest.fixture
def frame_handler(frame_serializer, host):
    yield FrameHandler(frame_serializer, host, Mock())


@pytest.fixture
def rx(frame_handler, frame_serializer):
    def inner(name: str, **kwargs):
        frame = Packet(name, **kwargs)
        frame_handler.process_packet(frame_serializer.to_bytes(frame))

    yield inner


@pytest.fixture
def tx(host, frame_handler, frame_serializer, device):
    def inner(name: str, **kwargs):
        frame = Packet(name, **kwargs)
        assert device.free_buffer() == [frame_serializer.to_bytes(frame)]

    yield inner


def test_ack_frame(rx, tx):
    rx('ACK')


def test_nak_frame(rx, tx):
    rx('NAK')


def test_can_frame(rx, tx):
    rx('CAN')


def test_valid_data_frame(rx, tx):
    rx('Data', type=FrameType.REQ, command=[], checksum=0xFD)
    tx('ACK')


def test_invalid_data_frame(rx, tx):
    rx('Data', type=FrameType.REQ, command=[], checksum=0x00)
    tx('NAK')
