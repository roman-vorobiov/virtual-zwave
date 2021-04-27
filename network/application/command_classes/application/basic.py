from ..command_class import CommandClass, command_class
from ..security_level import SecurityLevel
from ...channel import Channel
from ...request_context import Context

from network.protocol import Command

from typing import Dict, Tuple


MappedInfo = Tuple[int, str, dict]


@command_class('COMMAND_CLASS_BASIC', version=1)
class Basic1(CommandClass):
    advertise_in_nif = False

    def __init__(self, channel: Channel, required_security: SecurityLevel, mapping: Dict[str, MappedInfo]):
        super().__init__(channel, required_security)

        self.mapping = mapping

    def handle_command(self, command: Command, context: Context):
        class_id, command_name, args = self.mapping[command.get_meta('name')]
        self.resolve_args(args, command)

        mapped_cc = self.channel.get_command_class(class_id)
        mapped_command = mapped_cc.make_command(command_name, **args)
        mapped_cc.handle_command(mapped_command, context.copy(respond_with_basic=True))

    def send_report(self, context: Context, command: Command):
        class_id, command_name, args = self.mapping['BASIC_REPORT']
        self.resolve_args(args, command)

        self.send_command(context.copy(respond_with_basic=False), 'BASIC_REPORT', **args)

    @classmethod
    def resolve_args(cls, args: dict, command: Command):
        for key, value in args.items():
            if isinstance(value, str) and value.startswith("$"):
                args[key] = getattr(command, value[1:])
