from ..command_class import CommandClass, command_class
from ..security_level import SecurityLevel
from ...channel import Channel
from ...request_context import Context

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_ZWAVEPLUS_INFO', version=2)
class ZWavePlusInfo2(CommandClass):
    def __init__(
        self,
        channel: Channel,
        required_security: SecurityLevel,
        zwave_plus_version: int,
        role_type: int,
        node_type: int,
        installer_icon_type: int,
        user_icon_type: int
    ):
        super().__init__(channel, required_security)

        self.zwave_plus_version = zwave_plus_version
        self.role_type = role_type
        self.node_type = node_type
        self.installer_icon_type = installer_icon_type
        self.user_icon_type = user_icon_type

    @visit('ZWAVEPLUS_INFO_GET')
    def handle_info_get(self, command: Command, context: Context):
        self.send_info_report(context)

    def send_info_report(self, context: Context):
        self.send_command(context, 'ZWAVEPLUS_INFO_REPORT',
                          zwave_plus_version=self.zwave_plus_version,
                          role_type=self.role_type,
                          node_type=self.node_type,
                          installer_icon_type=self.installer_icon_type,
                          user_icon_type=self.user_icon_type)
