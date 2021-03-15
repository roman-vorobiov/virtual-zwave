from ..node import Node
from zwave.protocol import Packet

from tools import Visitor, log_warning


class CommandClass(Visitor):
    def __init__(self, node: Node, class_id: int, version: int):
        self.node = node

        self.class_id = class_id
        self.version = version

    def handle_command(self, command: Packet):
        return self.visit(command)

    def send_command(self, name: str, **kwargs):
        self.node.send_command(name, **kwargs)

    def visit(self, command: Packet, *args, **kwargs):
        return self.visit_as(command, command.name, *args, **kwargs)

    def visit_default(self, command: Packet, *args, **kwargs):
        log_warning(f"Unhandled command: {command.class_id} {command.command_id}")
