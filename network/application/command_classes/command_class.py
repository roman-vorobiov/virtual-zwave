from .command_factory import make_command

from zwave.protocol import Packet, PacketVisitor

from tools import log_warning

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..node import Node


class CommandClass(PacketVisitor):
    class_name: str
    class_id: int

    def __init__(self, node: 'Node'):
        self.node = node

    def handle_command(self, source_id: int, command: Packet):
        return self.visit(command, source_id=source_id)

    def send_command(self, destination_id: int, command: Packet):
        self.node.send_command(destination_id, command)

    def visit_default(self, command: Packet, *args, **kwargs):
        log_warning(f"Unhandled command: {command.class_id} {command.name}")

    @classmethod
    def make_command(cls, command_name: str, **kwargs):
        return make_command(cls.class_id, command_name, **kwargs)


def command_class(class_id: int, class_name: str):
    def inner(cls):
        cls.class_id = class_id
        cls.class_name = class_name
        return cls

    return inner
