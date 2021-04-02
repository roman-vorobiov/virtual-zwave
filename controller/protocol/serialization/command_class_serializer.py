from .schema import PacketSchema
from .schema_builder import PacketSchemaBuilder
from .packet_from_bytes_converter import PacketFromBytesConverter
from .packet_to_bytes_converter import PacketToBytesConverter
from .exceptions import SerializationError

from common import Command, make_command

import re
from pampy import match, _, TAIL
from typing import Dict, List, Optional, Tuple


class CommandClassSerializer:
    def __init__(self, command_data: Dict[str, Dict[str, list]]):
        self.schemas_by_id: Dict[Tuple[int, int, Optional[int]], PacketSchema] = {}
        self.schemas_by_name: Dict[Tuple[str, int], PacketSchema] = {}

        factory = PacketSchemaBuilder()
        pattern = re.compile(r".+(\d+)")

        for name, commands in command_data.items():
            if name.startswith("_"):
                continue

            class_version = int(pattern.match(name).group(1))

            for command_name, data in commands.items():
                schema = factory.create_schema(command_name, data)

                class_id, command_id = self.get_id(data)

                self.schemas_by_id[(class_id, command_id, class_version)] = schema
                self.schemas_by_name[(command_name, class_version)] = schema

    def from_bytes(self, data: List[int], class_version: int) -> Command:
        class_id, command_id = self.get_id(data)

        if (schema := self.schemas_by_id.get((class_id, command_id, class_version))) is not None:
            command = PacketFromBytesConverter().create_object(schema, data)
            command.set_meta('name', schema.name)
            command.set_meta('class_id', class_id)
            command.set_meta('class_version', class_version)
            return command

        return make_command(class_id, str(command_id), class_version, data=data)

    def to_bytes(self, command: Command) -> List[int]:
        command_name = command.get_meta('name')
        class_version = command.get_meta('class_version')

        if (schema := self.schemas_by_name.get((command_name, class_version))) is not None:
            return PacketToBytesConverter().serialize_packet(schema, command)

        raise SerializationError(f"Unknown command '{command_name}'")

    @classmethod
    def get_id(cls, data: list) -> Tuple[int, Optional[int]]:
        return match(data,
                     [_, _, TAIL], lambda cc_id, cmd_id, tail: (cc_id, cmd_id),
                     [_], lambda cc_id: (cc_id, None))
