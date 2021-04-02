from ..packet import Packet, make_packet
from .schema import PacketSchema
from .schema_builder import PacketSchemaBuilder
from .packet_from_bytes_converter import PacketFromBytesConverter
from .packet_to_bytes_converter import PacketToBytesConverter
from .exceptions import SerializationError

from typing import Dict, List


class PacketSerializer:
    def __init__(self, packet_data: Dict[str, list]):
        self.schemas_by_id: Dict[int, PacketSchema] = {}
        self.schemas_by_name: Dict[str, PacketSchema] = {}

        factory = PacketSchemaBuilder()

        for name, data in packet_data.items():
            if name.startswith("_"):
                continue

            schema = factory.create_schema(name, data)

            packet_id = data[0]

            self.schemas_by_id[packet_id] = schema
            self.schemas_by_name[name] = schema

    def from_bytes(self, packet: List[int]) -> Packet:
        packet_id = packet[0]

        if (packet_schema := self.schemas_by_id.get(packet_id)) is not None:
            return PacketFromBytesConverter().create_packet(packet_schema, packet)

        return make_packet('unknown', data=packet)

    def to_bytes(self, packet: Packet) -> List[int]:
        packet_name = packet.get_meta('name')

        if (packet_schema := self.schemas_by_name.get(packet_name)) is not None:
            return PacketToBytesConverter().serialize_packet(packet_schema, packet)

        raise SerializationError(f"Unknown packet '{packet_name}'")
