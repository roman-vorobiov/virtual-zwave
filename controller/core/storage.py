from tools import Resources

from typing import List


def from_string(value: str) -> List[int]:
    return [int(byte, base=16) for byte in value.split(' ')]


class Storage:
    def __init__(self, config: Resources):
        self.config = config
        self.data = []

        self.reset()

    def get(self, offset: int, length: int) -> List[int]:
        return self.data[offset:(offset + length)]

    def reset(self):
        self.data = [0xFF] * 0x100

        self.initialize_public_key()
        self.initialize_private_key()

    def initialize_public_key(self):
        self.data[0x23:0x43] = from_string(self.config['PUBLIC_KEY'])

    def initialize_private_key(self):
        self.data[0x43:0x63] = from_string(self.config['PRIVATE_KEY'])
