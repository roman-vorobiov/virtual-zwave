from ..command_class import CommandClass, command_class
from ...node import Node

from common import Command

from tools import visit


@command_class('COMMAND_CLASS_BASIC')
class Basic(CommandClass):
    def __init__(self, node: Node, value=0xFE):
        super().__init__(node)

        self.value = value

    @visit('BASIC_SET')
    def handle_set(self, command: Command, source_id: int):
        self.value = command.value

    @visit('BASIC_GET')
    def handle_get(self, command: Command, source_id: int):
        self.send_report(destination_id=source_id)

    def send_report(self, destination_id: int):
        command = self.make_command('BASIC_REPORT',
                                    value=self.value)

        self.send_command(destination_id, command)
