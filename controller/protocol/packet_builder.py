from tools import log_error

from enum import IntEnum
from typing import List, Optional


Bytes = List[int]


class States(IntEnum):
    IDLE = 0
    READ_LENGTH = 1
    READ_BYTES = 2
    READ_CHECKSUM = 3


class PacketBuilder:
    def __init__(self):
        self.buffer = []
        self.current_state = States.IDLE
        self.current_length = 0

    def reset(self):
        self.__init__()

    def process(self, byte: int) -> Optional[Bytes]:
        handlers = {
            States.IDLE:          self.process_idle,
            States.READ_LENGTH:   self.process_read_length,
            States.READ_BYTES:    self.process_read_bytes,
            States.READ_CHECKSUM: self.process_read_checksum,
        }

        self.buffer.append(byte)

        handler = handlers[self.current_state]
        return handler(byte)

    def dispatch(self) -> Bytes:
        result, self.buffer = self.buffer, []
        return result

    def discard(self):
        log_error("Discarded {:02x}".format(self.buffer[0]))
        self.buffer = []

    def process_idle(self, byte: int) -> Optional[Bytes]:
        if byte == 0x01:
            self.current_state = States.READ_LENGTH
        elif byte in (0x06, 0x15, 0x18):
            return self.dispatch()
        else:
            self.discard()

    def process_read_length(self, byte: int):
        self.current_length = byte - 1
        self.current_state = States.READ_BYTES

    def process_read_bytes(self, byte: int):
        self.current_length -= 1

        if self.current_length == 0:
            self.current_state = States.READ_CHECKSUM

    def process_read_checksum(self, byte: int) -> Optional[Bytes]:
        result = self.dispatch()
        self.current_state = States.IDLE
        return result
