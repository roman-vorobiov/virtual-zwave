from zwave.protocol.packet_builder import Bytes

from abc import ABC, abstractmethod
from typing import Iterator


class Device(ABC):
    @abstractmethod
    def poll(self) -> Iterator[Bytes]:
        pass

    @abstractmethod
    def send_data(self, data: Bytes):
        pass
