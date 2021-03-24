from ..command_class import CommandClass, command_class
from ...node import Node
from zwave.protocol import Packet

from tools import visit


@command_class('COMMAND_CLASS_ZWAVEPLUS_INFO')
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
        super().__init__(node)

        self.zwave_plus_version = zwave_plus_version
        self.role_type = role_type
        self.node_type = node_type
        self.installer_icon_type = installer_icon_type
        self.user_icon_type = user_icon_type

    @visit('ZWAVEPLUS_INFO_GET')
    def handle_info_get(self, command: Packet, source_id: int):
        self.send_info_report(destination_id=source_id)

    def send_info_report(self, destination_id: int):
        command = self.make_command('ZWAVEPLUS_INFO_REPORT',
                                    zwave_plus_version=self.zwave_plus_version,
                                    role_type=self.role_type,
                                    node_type=self.node_type,
                                    installer_icon_type=self.installer_icon_type,
                                    user_icon_type=self.user_icon_type)

        self.send_command(destination_id, command)
