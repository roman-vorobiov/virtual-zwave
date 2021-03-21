from ..command_class import CommandClass, command_class
from ...node import Node

from zwave.protocol import Packet

from tools import visit


@command_class(0x20, 'COMMAND_CLASS_BASIC')
class Basic(CommandClass):
    def __init__(self, node: Node):
        super().__init__(node)

        self.value = 0xFE

    @visit('BASIC_SET')
    def handle_set(self, command: Packet, source_id: int):
        self.value = command.value

    @visit('BASIC_GET')
    def handle_get(self, command: Packet, source_id: int):
        self.send_report(destination_id=source_id)

    def send_report(self, destination_id: int):
        command = self.make_command('BASIC_REPORT',
                                    value=self.value)

        self.send_command(destination_id, command)