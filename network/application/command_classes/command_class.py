from .command_class_factory import command_class_factory

from network.resources import CONSTANTS
from network.protocol import Command, CommandVisitor, make_command

from tools import Serializable, log_warning

from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ..node import Channel


class CommandClass(Serializable, CommandVisitor):
    class_id: int
    class_version: int

    def __init__(self, channel: 'Channel'):
        self.channel = channel

    def __getstate__(self):
        state = {'class_version': self.class_version, **self.__dict__}
        del state['channel']
        return state

    @property
    def node(self):
        return self.channel.node

    @property
    def context(self):
        return self.node.context

    def update_context(self, **kwargs):
        return self.node.update_context(**kwargs)

    def handle_command(self, command: Command):
        return self.visit(command)

    def send_command(self, _command: Union[Command, str], **kwargs):
        if type(_command) is str:
            _command = self.make_command(_command, **kwargs)

        self.channel.send_command(_command)

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
