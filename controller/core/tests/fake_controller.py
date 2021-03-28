from controller.core import Controller

from controller.protocol.packet_builder import Bytes

from tools import empty_async_generator

from typing import AsyncIterator, List


class FakeController(Controller):
    def __init__(self):
        self.tx_buffer = []

    @empty_async_generator
    async def poll(self) -> AsyncIterator[Bytes]:
        pass

    def send_data(self, data: Bytes):
        self.tx_buffer.append(data)

    def free_buffer(self) -> List[int]:
        self.tx_buffer, old_buffer = [], self.tx_buffer
        return old_buffer
