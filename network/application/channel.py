from .command_classes import CommandClass

from network.protocol import Command

from tools import Serializable, log_warning

from typing import TYPE_CHECKING, Dict, List, Type, TypeVar


if TYPE_CHECKING:
    from .node import Node


T = TypeVar('T', bound=CommandClass)


class Channel(Serializable):
    def __init__(self, node: 'Node', generic: int, specific: int):
        self.node = node

        self.generic = generic
        self.specific = specific

        self.command_classes: Dict[int, CommandClass] = {}

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['node']
        return state

    @property
    def endpoint(self):
        return self.node.channels.index(self)

    def add_command_class(self, cls: Type[T], **kwargs) -> T:
        cc = cls(self, **kwargs)
        self.command_classes[cc.class_id] = cc
        return cc

    def handle_command(self, data: List[int]):
        class_id = data[0]

        if (command_class := self.command_classes.get(class_id)) is not None:
            command = self.node.serializer.from_bytes(data, command_class.class_version)
            command_class.handle_command(command)
        else:
            log_warning(f"Channel does not support command class {class_id}")

    def send_command(self, command: Command):
        data = self.node.serializer.to_bytes(command)

        if self.endpoint == 0:
            self.node.send_command(data)
        else:
            multi_channel_cc = self.node.channels[0].command_classes[0x60]
            multi_channel_cc.send_encapsulated_command(self.endpoint, data)
