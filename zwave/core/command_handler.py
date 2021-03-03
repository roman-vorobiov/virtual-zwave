from .request_manager import RequestManager

from zwave.protocol import Packet, PacketVisitor
from zwave.protocol.serialization import PacketSerializer

from typing import List


class CommandHandler(PacketVisitor):
    def __init__(self, command_serializer: PacketSerializer, request_manager: RequestManager):
        self.command_serializer = command_serializer
        self.request_manager = request_manager

    def process_packet(self, packet: List[int]):
        command = self.command_serializer.from_bytes(packet)
        self.visit(command)

    def visit_default(self, packet: Packet, *args, **kwargs):
        print(packet.name, packet.fields)
