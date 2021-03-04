from tools import Visitor

from typing import Any


class Packet:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.fields = kwargs

    def __eq__(self, other: 'Packet'):
        return self.name == other.name and self.fields == other.fields

    def __getattr__(self, field_name: str) -> Any:
        return self.fields[field_name]

    def __getitem__(self, field_name: str) -> Any:
        return self.fields[field_name]

    def __setitem__(self, field_name: str, value: Any):
        self.fields[field_name] = value


class PacketVisitor(Visitor):
    def visit(self, packet: Packet, *args, **kwargs):
        return self.visit_as(packet, packet.name, *args, **kwargs)

