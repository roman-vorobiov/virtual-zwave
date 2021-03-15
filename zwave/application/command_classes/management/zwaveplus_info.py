from ..command_class import CommandClass
from ...node import Node
from zwave.protocol import Packet

from tools import visit


class ZWavePlusInfo(CommandClass):
    def __init__(
        self,
        node: Node,
        zwave_plus_version: int,
        role_type: int,
        node_type: int,
        installer_icon_type: int,
        user_icon_type: int
    ):
        super().__init__(node, 0x5E, version=1)

        self.zwave_plus_version = zwave_plus_version
        self.role_type = role_type
        self.node_type = node_type
        self.installer_icon_type = installer_icon_type
        self.user_icon_type = user_icon_type

    @visit('ZWAVEPLUS_INFO_GET')
    def handle_info_get(self, command: Packet):
        self.send_info_report()

    def send_info_report(self):
        self.send_command('ZWAVEPLUS_INFO_REPORT',
                          zwave_plus_version=self.zwave_plus_version,
                          role_type=self.role_type,
                          node_type=self.node_type,
                          installer_icon_type=self.installer_icon_type,
                          user_icon_type=self.user_icon_type)
