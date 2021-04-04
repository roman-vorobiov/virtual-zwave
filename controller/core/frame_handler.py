from .host import Host
from .command_handler import CommandHandler
from .utils import is_valid_checksum

from controller.protocol import Packet, PacketVisitor, PacketSerializer

from tools import visit, log_warning

from typing import List


class FrameHandler(PacketVisitor):
    def __init__(self, frame_serializer: PacketSerializer, host: Host, command_handler: CommandHandler):
        self.frame_serializer = frame_serializer
        self.host = host
        self.command_handler = command_handler

    def process_packet(self, packet: List[int]):
        packet = self.frame_serializer.from_bytes(packet)
        self.visit(packet)

    @visit('Data')
    def handle_data_frame(self, packet: Packet):
        if is_valid_checksum(packet):
            self.host.send_ack()
            self.command_handler.process_packet(packet.command)
        else:
            log_warning("Invalid checksum")
            self.host.send_nak()

    @visit('NAK', 'CAN')
    def handle_nak_can_frame(self, packet: Packet):
        log_warning(f"{packet.get_meta('name')} received")

    @visit('ACK')
    def handle_ack_frame(self, packet: Packet):
        self.host.unblock()
