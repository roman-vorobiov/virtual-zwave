from enum import IntEnum, IntFlag


class AddNodeMode(IntEnum):
    ANY = 0x01
    CONTROLLER = 0x02
    SLAVE = 0x03
    EXISTING = 0x04
    STOP = 0x05
    STOP_FAILED = 0x06
    HOME_ID = 0x08
    SMART_START = 0x09


class AddNodeOptions(IntFlag):
    NETWORK_WIDE = 0x40
    NORMAL_POWER = 0x80


class AddNodeStatus(IntEnum):
    LEARN_READY = 0x01
    NODE_FOUND = 0x02
    ADDING_SLAVE = 0x03
    ADDING_CONTROLLER = 0x04
    PROTOCOL_DONE = 0x05
    DONE = 0x06
    FAILED = 0x07
    NOT_PRIMARY = 0x23
