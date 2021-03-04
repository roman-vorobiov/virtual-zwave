from .device import Device
from .utils import calculate_checksum

from zwave.protocol import Packet
from zwave.protocol.frames.data import FrameType
from zwave.protocol.serialization import PacketSerializer

from typing import List


class Host:
    def __init__(self, frame_serializer: PacketSerializer, device: Device):
        self.frame_serializer = frame_serializer
        self.device = device

    def send_ack(self):
        frame = Packet('ACK')
        self.send_frame(frame)

    def send_nak(self):
        frame = Packet('NAK')
        self.send_frame(frame)

    def send_can(self):
        frame = Packet('CAN')
        self.send_frame(frame)

    def send_data(self, frame_type: FrameType, command: List[int]):
        frame = Packet('Data', type=frame_type.value, command=command, checksum=0xFF)
        frame['checksum'] = calculate_checksum(frame)
        self.send_frame(frame)

    def send_frame(self, frame: Packet):
        data = self.frame_serializer.to_bytes(frame)
        self.device.send_data(data)
