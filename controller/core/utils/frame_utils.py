from controller.protocol import Packet

from tools import calculate_lrc


def calculate_checksum(data_frame: Packet) -> int:
    return calculate_lrc([len(data_frame.command) + 2, data_frame.type, *data_frame.command], seed=0xFF)


def is_valid_checksum(packet: Packet) -> bool:
    return packet.checksum == calculate_checksum(packet)
