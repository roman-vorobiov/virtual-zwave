from ..packet import Packet
from .schema import PacketSchema
from .schema_builder import PacketSchemaBuilder
from .packet_from_bytes_converter import PacketFromBytesConverter
from .packet_to_bytes_converter import PacketToBytesConverter
from .exceptions import SerializationError

from typing import Dict, List, Any


class PacketSerializer:
    def __init__(self, packet_data: Dict[str, list]):
        self.schemas_by_id: Dict[Any, PacketSchema] = {}
        self.schemas_by_name: Dict[str, PacketSchema] = {}

        factory = PacketSchemaBuilder()

        for name, data in packet_data.items():
            if name.startswith("_"):
                continue

            schema = factory.create_schema(name, data)

            self.schemas_by_id[self.get_id(data)] = schema
            self.schemas_by_name[name] = schema

    def from_bytes(self, packet: List[int]) -> Packet:
        if (packet_schema := self.schemas_by_id.get(self.get_id(packet))) is not None:
            return PacketFromBytesConverter().create_packet(packet_schema, packet)

        return Packet(name='unknown', data=packet)

    def to_bytes(self, packet: Packet) -> List[int]:
        if (packet_schema := self.schemas_by_name.get(packet.name)) is not None:
            return PacketToBytesConverter().serialize_packet(packet_schema, packet)

        raise SerializationError(f"Unknown packet '{packet.name}'")

    def get_id(self, packet_or_schema: list):
        return packet_or_schema[0]


class CommandClassSerializer(PacketSerializer):
    def get_id(self, packet_or_schema: list):
        if len(packet_or_schema) == 1:
            return packet_or_schema[0]
        else:
            return packet_or_schema[0], packet_or_schema[1]

    def from_bytes(self, packet: List[int]) -> Packet:
        command = super().from_bytes(packet)

        command.class_id = packet[0]
        if len(packet) > 1:
            command.command_id = packet[1]

        return command
