from .command_class_factory import command_class_factory

from network.resources import CONSTANTS

from common import Command, CommandVisitor, make_command

from tools import serializable, log_warning

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..node import Channel


@serializable(excluded_fields=['channel'], class_fields=['class_version'])
class CommandClass(CommandVisitor):
    class_id: int
    class_version: int

    def __init__(self, channel: 'Channel'):
        self.channel = channel

    @property
    def node(self):
        return self.channel.node

    def handle_command(self, source_id: int, command: Command):
        return self.visit(command, source_id=source_id)

    def send_command(self, destination_id: int, command: Command):
        self.channel.send_command(destination_id, command)

    def visit_default(self, command: Command, *args, **kwargs):
        log_warning(f"Unhandled command: {command.get_meta('name')}")

    @classmethod
    def make_command(cls, command_name: str, **kwargs) -> Command:
        return make_command(cls.class_id, command_name, cls.class_version, **kwargs)


def command_class(class_name: str, version=1):
    def inner(cls):
        cls.class_id = CONSTANTS['CommandClassId'][class_name]
        cls.class_version = version

        command_class_factory.register(cls)

        return cls

    return inner
