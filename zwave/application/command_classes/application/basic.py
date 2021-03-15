from ..command_class import CommandClass
from ...node import Node
from zwave.protocol import Packet

from tools import visit


class Basic(CommandClass):
    def __init__(self, node: Node):
        super().__init__(node, 0x20, version=1)
        self.value = 0xFE

    @visit('BASIC_SET')
    def handle_set(self, command: Packet):
        self.value = command.value

    @visit('BASIC_GET')
    def handle_get(self, command: Packet):
        self.send_report()

    def send_report(self):
        self.send_command('BASIC_REPORT',
                          value=self.value)
