from typing import List


def dump_hex(data: List[int]):
    return "[{}]".format(" ".join("{:02x}".format(byte) for byte in data))
