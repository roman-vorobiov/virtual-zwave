from network.protocol import make_command


COMMAND_CLASS_BASIC_1 = [
    ([0x20, 0x01, 0x01], make_command(0x20, 'BASIC_SET', 1, value=1)),
    ([0x20, 0x02], make_command(0x20, 'BASIC_GET', 1)),
    ([0x20, 0x03, 0x01], make_command(0x20, 'BASIC_REPORT', 1, value=1))
]

COMMAND_CLASS_SWITCH_BINARY_1 = [
    ([0x25, 0x01, 0x01], make_command(0x25, 'SWITCH_BINARY_SET', 1, value=1)),
    ([0x25, 0x02], make_command(0x25, 'SWITCH_BINARY_GET', 1)),
    ([0x25, 0x03, 0x01], make_command(0x25, 'SWITCH_BINARY_REPORT', 1, value=1))
]

COMMAND_CLASS_SWITCH_BINARY_2 = [
    (
        [0x25, 0x01, 0x01, 0x02],
        make_command(0x25, 'SWITCH_BINARY_SET', 2, value=1, duration=2)
    ),
    (
        [0x25, 0x02],
        make_command(0x25, 'SWITCH_BINARY_GET', 2)
    ),
    (
        [0x25, 0x03, 0x01, 0x02, 0x03],
        make_command(0x25, 'SWITCH_BINARY_REPORT', 2, current_value=1, target_value=2, duration=3)
    )
]

APPLICATION = [
    *COMMAND_CLASS_BASIC_1,
    *COMMAND_CLASS_SWITCH_BINARY_1,
    *COMMAND_CLASS_SWITCH_BINARY_2,
]
