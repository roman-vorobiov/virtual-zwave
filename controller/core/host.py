from .controller import Controller
from .utils import calculate_checksum

from controller.protocol import Packet, make_packet
from controller.protocol.frames.data import FrameType
from controller.protocol.serialization import PacketSerializer

from collections import deque
from typing import List


class TxBuffer:
    def __init__(self, device: Controller):
        self.device = device
        self.queue = deque()
        self.blocked = False

    def unblock(self):
        while len(self.queue) != 0:
            data, blocking = self.queue.popleft()
            self.send_data(data, blocking)
            if blocking:
                break
        else:
            self.blocked = False

    def put(self, data: List[int], blocking: bool):
        if self.blocked:
            self.queue.append((data, blocking))
        else:
            self.send_data(data, blocking)

    def send_data(self, data: List[int], blocking: bool):
        self.device.send_data(data)
        self.blocked = blocking


class Host:
    def __init__(self, frame_serializer: PacketSerializer, device: Controller):
        self.frame_serializer = frame_serializer
        self.tx_buffer = TxBuffer(device)

    def unblock(self):
        self.tx_buffer.unblock()

    def send_ack(self):
        frame = make_packet('ACK')
        self.send_frame(frame, False)

    def send_nak(self):
        frame = make_packet('NAK')
        self.send_frame(frame, False)

    def send_can(self):
        frame = make_packet('CAN')
        self.send_frame(frame, False)

    def send_data(self, frame_type: FrameType, command: List[int]):
        frame = make_packet('Data', type=frame_type.value, command=command, checksum=0xFF)
        frame.checksum = calculate_checksum(frame)
        self.send_frame(frame, True)

    def send_frame(self, frame: Packet, blocking: bool):
        data = self.frame_serializer.to_bytes(frame)
        self.tx_buffer.put(data, blocking)
