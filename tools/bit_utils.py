from typing import Iterable, Iterator


def each_bit(mask: int, start=0) -> Iterator[int]:
    bit = start
    while mask:
        if (mask % 2) != 0:
            yield bit
        mask >>= 1
        bit += 1


def create_mask(bits: Iterable, start=0):
    mask = 0
    for bit in bits:
        mask |= 1 << (bit - start)

    return mask
