from .command_classes import CommandClass

from network.protocol import Command, CommandClassSerializer

from tools import Serializable, log_warning

from typing import TYPE_CHECKING, Dict, List


if TYPE_CHECKING:
    from .node import Node


class Channel(Serializable):
    def __init__(self, node: 'Node', serializer: CommandClassSerializer, generic: int, specific: int):
        self.node = node
        self.serializer = serializer

        self.generic = generic
        self.specific = specific

        self.command_classes: Dict[int, CommandClass] = {}

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['node']
        del state['serializer']
        return state

    @property
    def endpoint(self):
        return self.node.channels.index(self)

    def add_command_class(self, cc: CommandClass):
        self.command_classes[cc.class_id] = cc

    def handle_command(self, source_id: int, data: List[int]):
        class_id = data[0]

        if (command_class := self.command_classes.get(class_id)) is not None:
            command = self.serializer.from_bytes(data, command_class.class_version)
            command_class.handle_command(source_id, command)
        else:
            log_warning(f"Channel does not support command class {class_id}")

    def send_command(self, destination_id: int, command: Command):
        data = self.serializer.to_bytes(command)

        if self.endpoint == 0:
            self.node.send_command(destination_id, data)
        else:
            multi_channel_cc = self.node.channels[0].command_classes[0x60]
            multi_channel_cc.send_encapsulated_command(destination_id, self.endpoint, data)
