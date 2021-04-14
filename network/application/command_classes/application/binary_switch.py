from ..command_class import CommandClass, command_class
from ...channel import Channel
from ...request_context import Context

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_SWITCH_BINARY', version=1)
class BinarySwitch1(CommandClass):
    def __init__(self, channel: Channel, value=0xFE):
        super().__init__(channel)

        self.value = value

    @visit('SWITCH_BINARY_SET')
    def handle_set(self, command: Command, context: Context):
        self.value = command.value
        self.on_state_change()

    @visit('SWITCH_BINARY_GET')
    def handle_get(self, command: Command, context: Context):
        self.send_report(context)

    def send_report(self, context: Context):
        self.send_command(context, 'SWITCH_BINARY_REPORT', value=self.value)
