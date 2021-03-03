from typing import List


def calculate_lrc(packet: List[int], seed: int) -> int:
    checksum = seed

    for byte in packet:
        checksum ^= byte

    return checksum
