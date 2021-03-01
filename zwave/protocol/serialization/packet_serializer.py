from ..packet import Packet
from .schema import PacketSchema
from .schema_builder import PacketSchemaBuilder
from .packet_from_bytes_converter import PacketFromBytesConverter
from .packet_to_bytes_converter import PacketToBytesConverter

from typing import Dict, List, Optional


class PacketSerializer:
    def __init__(self, packet_data: Dict[str, list]):
        self.schemas_by_byte: Dict[int, PacketSchema] = {}
        self.schemas_by_name: Dict[str, PacketSchema] = {}

        factory = PacketSchemaBuilder()

        for name, data in packet_data.items():
            schema = factory.create_schema(name, data)

            self.schemas_by_byte[data[0]] = schema
            self.schemas_by_name[name] = schema

    def from_bytes(self, packet: List[int]) -> Optional[Packet]:
        if (packet_schema := self.schemas_by_byte.get(packet[0])) is not None:
            return PacketFromBytesConverter().create_packet(packet_schema, packet)

        print("Unknown packet")

    def to_bytes(self, packet: Packet) -> List[int]:
        if (packet_schema := self.schemas_by_name.get(packet.name)) is not None:
            return PacketToBytesConverter().serialize_packet(packet_schema, packet)

        print("Unknown packet")
