from .fixtures import *

from zwave.protocol.frames.data import FrameType


def test_send_non_blocking(host, device):
    host.send_ack()
    host.send_ack()
    host.send_ack()

    assert device.free_buffer() == [
        [0x06],
        [0x06],
        [0x06]
    ]


def test_send_blocking(host, device):
    host.send_data(FrameType.REQ, [0x00])
    host.send_data(FrameType.REQ, [0x00])
    host.send_ack()
    host.send_data(FrameType.REQ, [0x00])

    assert device.free_buffer() == [
        [0x01, 0x03, 0x00, 0x00, 0xFC]
    ]

    host.unblock()
    assert device.free_buffer() == [
        [0x01, 0x03, 0x00, 0x00, 0xFC]
    ]

    host.unblock()
    assert device.free_buffer() == [
        [0x06],
        [0x01, 0x03, 0x00, 0x00, 0xFC]
    ]
