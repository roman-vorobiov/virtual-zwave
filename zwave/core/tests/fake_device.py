from zwave.core import Device

from zwave.protocol.packet_builder import Bytes

from typing import Iterator, List


class FakeDevice(Device):
    def __init__(self):
        self.tx_buffer = []

    def poll(self) -> Iterator[Bytes]:
        yield from []

    def send_data(self, data: Bytes):
        self.tx_buffer.append(data)

    def free_buffer(self) -> List[int]:
        self.tx_buffer, old_buffer = [], self.tx_buffer
        return old_buffer
