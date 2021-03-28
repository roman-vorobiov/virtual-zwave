from enum import IntEnum, IntFlag


class RemoveNodeMode(IntEnum):
    ANY = 0x01
    CONTROLLER = 0x02
    SLAVE = 0x03
    STOP = 0x05


class RemoveNodeOptions(IntFlag):
    NETWORK_WIDE = 0x40
    NORMAL_POWER = 0x80


class RemoveNodeStatus(IntEnum):
    LEARN_READY = 0x01
    NODE_FOUND = 0x02
    REMOVING_SLAVE = 0x03
    REMOVING_CONTROLLER = 0x04
    DONE = 0x06
    FAILED = 0x07
