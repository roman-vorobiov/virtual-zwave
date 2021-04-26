from .command_classes import CommandClass, SecurityLevel
from .request_context import Context
from .utils import AssociationsManager, AssociationGroup

from network.protocol import Command, log_command
from network.resources import CONSTANTS

from tools import Serializable, log_warning

from typing import TYPE_CHECKING, Dict, List, Optional, Type, TypeVar


if TYPE_CHECKING:
    from .node import Node
    from .command_classes.transport_encapsulation import MultiChannel3
    from .command_classes.transport_encapsulation import Security1


T = TypeVar('T', bound=CommandClass)


class Channel(Serializable):
    def __init__(self, node: 'Node', generic: int, specific: int, association_groups: List[AssociationGroup] = None):
        self.node = node
        self.associations = AssociationsManager(association_groups or [])

        self.generic = generic
        self.specific = specific

        self.command_classes: Dict[int, T] = {}

    def __getstate__(self):
        return {
            'endpoint': self.endpoint,
            'generic': self.generic,
            'specific': self.specific,
            'association_groups': self.associations.groups,
            'command_classes': list(self.command_classes.values())
        }

    @property
    def endpoint(self):
        return self.node.channels.index(self)

    def reset(self):
        self.associations.clear_all()

        for cc in self.command_classes.values():
            cc.reset_state()

    def add_command_class(self, cls: Type[T], required_security=SecurityLevel.NONE, /, **kwargs) -> T:
        cc = cls(self, required_security, **kwargs)
        self.command_classes[cc.class_id] = cc
        return cc

    def get_command_class(self, class_id) -> Optional['CommandClass']:
        return self.command_classes.get(class_id)

    def get_multi_channel_command_class(self) -> Optional['MultiChannel3']:
        class_id = CONSTANTS['CommandClassId']['COMMAND_CLASS_MULTI_CHANNEL']
        return self.get_command_class(class_id)

    def get_security_command_class(self) -> Optional['Security1']:
        class_id = CONSTANTS['CommandClassId']['COMMAND_CLASS_SECURITY']
        return self.get_command_class(class_id)

    def handle_command(self, data: List[int], context: Context):
        class_id = data[0]

        if (command_class := self.get_command_class(class_id)) is not None:
            command = self.node.serializer.from_bytes(data, command_class.class_version)
            log_command(context.node_id, context.endpoint, self.node.node_id, self.endpoint, command)
            command_class.handle_command(command, context)
        else:
            log_warning("Channel does not support command class 0x{:02X}".format(class_id))

    def send_command(self, command: Command, context: Context):
        log_command(self.node.node_id, self.endpoint, context.node_id, context.endpoint, command)
        data = self.node.serializer.to_bytes(command)

        if self.endpoint == 0 and context.endpoint == 0:
            self.node.send_command(data, context)
        else:
            multi_channel_cc = self.node.channels[0].get_multi_channel_command_class()
            multi_channel_cc.send_encapsulated_command(context, self.endpoint, data)

    def on_state_change(self):
        self.node.save()
        self.node.state_observer.on_channel_updated(self)
