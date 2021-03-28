from .command_class_factory import command_class_factory

from network.resources import CONSTANTS

from common import Command, CommandVisitor, make_command

from tools import log_warning

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..node import Node


class CommandClass(CommandVisitor):
    class_id: int

    def __init__(self, node: 'Node'):
        self.node = node

    def handle_command(self, source_id: int, command: Command):
        return self.visit(command, source_id=source_id)

    def send_command(self, destination_id: int, command: Command):
        self.node.send_command(destination_id, command)

    def visit_default(self, command: Command, *args, **kwargs):
        log_warning(f"Unhandled command: {command.get_meta('name')}")

    @classmethod
    def make_command(cls, command_name: str, **kwargs):
        return make_command(cls.class_id, command_name, **kwargs)


def command_class(class_name: str):
    def inner(cls):
        cls.class_id = CONSTANTS['CommandClassId'][class_name]
        command_class_factory.register(class_name, cls)
        return cls

    return inner
