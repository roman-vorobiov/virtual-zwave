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
    AVREMOTE = 0x0A
    AVDEVICE = 0x0B
