from ..command_class import CommandClass, command_class
from ...channel import Channel

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_BASIC', version=1)
class Basic1(CommandClass):
    def __init__(self, channel: Channel, value=0xFE):
        super().__init__(channel)

        self.value = value

    @visit('BASIC_SET')
    def handle_set(self, command: Command, source_id: int):
        self.value = command.value
        self.on_state_change()

    @visit('BASIC_GET')
    def handle_get(self, command: Command, source_id: int):
        self.send_report(destination_id=source_id)

    def send_report(self, destination_id: int):
        command = self.make_command('BASIC_REPORT',
                                    value=self.value)

        self.send_command(destination_id, command)
