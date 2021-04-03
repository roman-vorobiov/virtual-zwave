def each_bit(mask: int):
    bit = 0
    while mask:
        if (mask % 2) != 0:
            yield bit
        mask >>= 1
        bit += 1
