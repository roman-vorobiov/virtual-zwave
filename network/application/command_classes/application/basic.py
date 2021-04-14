from ..command_class import CommandClass, command_class
from ...channel import Channel
from ...request_context import Context

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_BASIC', version=1)
class Basic1(CommandClass):
    advertise_in_nif = False

    def __init__(self, channel: Channel, value=0xFE):
        super().__init__(channel)

        self.value = value

    @visit('BASIC_SET')
    def handle_set(self, command: Command, context: Context):
        self.value = command.value
        self.on_state_change()

    @visit('BASIC_GET')
    def handle_get(self, command: Command, context: Context):
        self.send_report(context)

    def send_report(self, context: Context):
        self.send_command(context, 'BASIC_REPORT', value=self.value)
