from .command_class_factory import command_class_factory
from ..request_context import Context

from network.resources import CONSTANTS
from network.protocol import Command, CommandVisitor, make_command

from tools import Serializable, log_warning

from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ..node import Channel


class CommandClass(Serializable, CommandVisitor):
    class_id: int
    class_version: int
    advertise_in_nif = True

    def __init__(self, channel: 'Channel'):
        self.channel = channel
        self.secure = False

    def __getstate__(self):
        state = self.__dict__.copy()
        state['class_version'] = self.class_version
        del state['channel']
        return state

    def mark_as_secure(self):
        self.secure = True

    @property
    def node(self):
        return self.channel.node

    def handle_command(self, command: Command, context: Context):
        self.visit(command, context)

    def send_command(self, _context: Context, _command: Union[Command, str], **kwargs):
        if type(_command) is str:
            _command = self.make_command(_command, **kwargs)

        self.channel.send_command(_command, _context)

    def on_state_change(self):
        self.node.save()
        self.node.notify_updated()

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
