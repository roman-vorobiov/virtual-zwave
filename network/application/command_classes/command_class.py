from .command_class_factory import command_class_factory
from .security_level import SecurityLevel
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

    def __init__(self, channel: 'Channel', required_security: SecurityLevel):
        self.channel = channel
        self.required_security = required_security

    def __getstate__(self):
        return {
            'class_id': self.class_id,
            'version': self.class_version,
            'required_security': self.required_security,
            'state': self.__getstate_impl__()
        }

    def __getstate_impl__(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if key not in {'channel', 'required_security'}}

    def reset_state(self):
        pass

    @property
    def supported_non_securely(self):
        if self.required_security == SecurityLevel.NONE:
            return True
        elif self.required_security == SecurityLevel.GRANTED:
            return not self.node.secure
        else:
            return False

    @property
    def node(self):
        return self.channel.node

    def handle_command(self, command: Command, context: Context):
        if self.supported_non_securely or context.secure:
            self.visit(command, context)
        else:
            log_warning("Incorrect security level")

    def send_command(self, context: Context, command: Union[Command, str], /, **kwargs):
        if type(command) is str:
            command = self.make_command(command, **kwargs)

        self.channel.send_command(command, context)

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
