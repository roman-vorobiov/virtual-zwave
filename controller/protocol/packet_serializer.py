from .packet import Packet, make_packet

from common.serialization import (
    Schema,
    SchemaBuilder,
    ObjectFromBytesConverter,
    ObjectToBytesConverter,
    SerializationError
)

from typing import Dict, List


class PacketSerializer:
    def __init__(self, data: Dict[str, list]):
        self.schemas_by_id: Dict[int, Schema] = {}
        self.schemas_by_name: Dict[str, Schema] = {}

        factory = SchemaBuilder()

        for name, data in data.items():
            if name.startswith("_"):
                continue

            schema = factory.create_schema(name, data)

            packet_id = data[0]

            self.schemas_by_id[packet_id] = schema
            self.schemas_by_name[name] = schema

    def from_bytes(self, packet: List[int]) -> Packet:
        packet_id = packet[0]

        if (schema := self.schemas_by_id.get(packet_id)) is not None:
            packet = ObjectFromBytesConverter().convert(schema, packet)
            packet.set_meta('name', schema.name)
            return packet

        return make_packet('unknown', data=packet)

    def to_bytes(self, packet: Packet) -> List[int]:
        packet_name = packet.get_meta('name')

        if (schema := self.schemas_by_name.get(packet_name)) is not None:
            return ObjectToBytesConverter().convert(schema, packet)

        raise SerializationError(f"Unknown packet '{packet_name}'")
