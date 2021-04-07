from network.protocol import make_command


COMMAND_CLASS_BASIC_1 = [
    ([0x20, 0x01, 0x01], make_command(0x20, 'BASIC_SET', 1, value=1)),
    ([0x20, 0x02], make_command(0x20, 'BASIC_GET', 1)),
    ([0x20, 0x03, 0x01], make_command(0x20, 'BASIC_REPORT', 1, value=1))
]

APPLICATION = [
    *COMMAND_CLASS_BASIC_1
]
