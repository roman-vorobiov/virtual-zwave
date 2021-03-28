from enum import IntEnum


class LibraryType(IntEnum):
    CONTROLLER_STATIC = 0x01
    CONTROLLER = 0x02
    SLAVE_ENHANCED = 0x03
    SLAVE = 0x04
    INSTALLER = 0x05
    SLAVE_ROUTING = 0x06
    CONTROLLER_BRIDGE = 0x07
    DUT = 0x08
    AV_REMOTE = 0x0A
    AV_DEVICE = 0x0B
