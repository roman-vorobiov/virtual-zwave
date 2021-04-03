from .fixtures.components import *

from controller.protocol.frames.data import FrameType


def test_send_non_blocking(host, controller):
    host.send_ack()
    host.send_ack()
    host.send_ack()

    assert controller.free_buffer() == [
        [0x06],
        [0x06],
        [0x06]
    ]


def test_send_blocking(host, controller):
    host.send_data(FrameType.REQ, [0x00])
    host.send_data(FrameType.REQ, [0x00])
    host.send_ack()
    host.send_data(FrameType.REQ, [0x00])

    assert controller.free_buffer() == [
        [0x01, 0x03, 0x00, 0x00, 0xFC]
    ]

    host.unblock()
    assert controller.free_buffer() == [
        [0x01, 0x03, 0x00, 0x00, 0xFC]
    ]

    host.unblock()
    assert controller.free_buffer() == [
        [0x06],
        [0x01, 0x03, 0x00, 0x00, 0xFC]
    ]
