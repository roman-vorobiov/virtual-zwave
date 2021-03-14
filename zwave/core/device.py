from zwave.protocol.packet_builder import Bytes

from abc import ABC, abstractmethod
from typing import AsyncIterator


class Device(ABC):
    @abstractmethod
    async def poll(self) -> AsyncIterator[Bytes]:
        pass

    @abstractmethod
    def send_data(self, data: Bytes):
        pass
