from .command_classes import CommandClass

from common import Command

from tools import serializable, log_warning

from typing import TYPE_CHECKING, Dict


if TYPE_CHECKING:
    from .node import Node


@serializable(excluded_fields=['node'])
class Channel:
    def __init__(self, node: 'Node', generic: int, specific: int):
        self.node = node

        self.generic = generic
        self.specific = specific

        self.command_classes: Dict[int, CommandClass] = {}

    @property
    def endpoint(self):
        return self.node.channels.index(self)

    def add_command_class(self, cc: CommandClass):
        self.command_classes[cc.class_id] = cc

    def handle_command(self, source_id: int, command: Command):
        class_id = command.get_meta('class_id')

        if (command_class := self.command_classes.get(class_id)) is not None:
            command_class.handle_command(source_id, command)
        else:
            log_warning(f"Channel does not support command class {class_id}")

    def send_command(self, destination_id: int, command: Command):
        if self.endpoint == 0:
            self.node.send_command(destination_id, command)
        else:
            multi_channel_cc = self.node.channels[0].command_classes[0x60]
            multi_channel_cc.send_encapsulated_command(destination_id, self.endpoint, command)
