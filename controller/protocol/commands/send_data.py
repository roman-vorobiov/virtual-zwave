from enum import IntEnum, IntFlag


class TransmitOptions(IntFlag):
    ACK = 0x01
    LOW_POWER = 0x02
    AUTO_ROUTE = 0x04
    FORCE_ROUTE = 0x08
    NO_ROUTE = 0x10
    EXPLORE = 0x20
    NO_RETRANSMIT = 0x40


class TransmitStatus(IntEnum):
    OK = 0x00
    NO_ACK = 0x01
    FAIL = 0x02
    NO_ROUTE = 0x04
