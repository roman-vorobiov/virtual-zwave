from .command_class_factory import command_class_factory
from .security_level import SecurityLevel
from ..request_context import Context

from network.resources import CONSTANTS
from network.protocol import Command, CommandVisitor, make_command

from tools import Serializable, create_marker, log_warning, VisitorMeta

from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ..node import Channel


CommandClassMetaBase, signal = create_marker('__signals__', '__signal__')


# The metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
class CommandClassMeta(CommandClassMetaBase, VisitorMeta):
    def __init__(cls, *args, **kwargs):
        type.__init__(cls, *args, **kwargs)

        CommandClassMetaBase.collect_markers(cls)
        VisitorMeta.collect_markers(cls)


class CommandClass(Serializable, CommandVisitor, metaclass=CommandClassMeta):
    class_id: int
    class_name: str
    class_version: int
    advertise_in_nif = True

    def __init__(self, channel: 'Channel', required_security: SecurityLevel):
        self.channel = channel
        self.required_security = required_security

    def __getstate__(self):
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'version': self.class_version,
            'required_security': self.required_security,
            'state': self.__getstate_impl__()
        }

    def __getstate_impl__(self) -> dict:
        state = self.__dict__.copy()
        del state['channel']
        del state['required_security']
        return state

    def reset_state(self):
        pass

    def update_state(self, **kwargs):
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

    def emit(self, command_name: str):
        command_id = CONSTANTS['CommandId'][self.class_name][command_name]

        for node_id, endpoints in self.channel.associations.find_targets(self.class_id, command_id):
            send_report = self.__signals__[command_name]
            for endpoint in endpoints:
                send_report(self, Context(node_id=node_id, endpoint=endpoint, secure=self.node.secure))

    def on_state_change(self):
        self.node.save()
        self.node.state_observer.on_command_class_updated(self)

    def visit_default(self, command: Command, command_name: str):
        log_warning(f"Unhandled command: {command_name}")

    @classmethod
    def make_command(cls, command_name: str, **kwargs) -> Command:
        return make_command(cls.class_id, command_name, cls.class_version, **kwargs)


def command_class(class_name: str, version=1):
    def inner(cls):
        cls.class_id = CONSTANTS['CommandClassId'][class_name]
        cls.class_name = class_name
        cls.class_version = version

        command_class_factory.register(cls)

        return cls

    return inner
