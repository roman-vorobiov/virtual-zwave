from ..command_class import CommandClass, command_class
from ...channel import Channel

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_ZWAVEPLUS_INFO', version=2)
class ZWavePlusInfo2(CommandClass):
    def __init__(
        self,
        channel: Channel,
        zwave_plus_version: int,
        role_type: int,
        node_type: int,
        installer_icon_type: int,
        user_icon_type: int
    ):
        super().__init__(channel)

        self.zwave_plus_version = zwave_plus_version
        self.role_type = role_type
        self.node_type = node_type
        self.installer_icon_type = installer_icon_type
        self.user_icon_type = user_icon_type

    @visit('ZWAVEPLUS_INFO_GET')
    def handle_info_get(self, command: Command):
        self.send_info_report()

    def send_info_report(self):
        command = self.make_command('ZWAVEPLUS_INFO_REPORT',
                                    zwave_plus_version=self.zwave_plus_version,
                                    role_type=self.role_type,
                                    node_type=self.node_type,
                                    installer_icon_type=self.installer_icon_type,
                                    user_icon_type=self.user_icon_type)

        self.send_command(command)
