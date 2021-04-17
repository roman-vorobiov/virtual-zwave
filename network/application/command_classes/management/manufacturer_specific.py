from ..command_class import CommandClass, command_class
from ..security_level import SecurityLevel
from ...channel import Channel
from ...request_context import Context

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_MANUFACTURER_SPECIFIC', version=1)
class ManufacturerSpecific1(CommandClass):
    def __init__(
        self,
        channel: Channel,
        required_security: SecurityLevel,
        manufacturer_id: int,
        product_type_id: int,
        product_id: int
    ):
        super().__init__(channel, required_security)

        self.manufacturer_id = manufacturer_id
        self.product_type_id = product_type_id
        self.product_id = product_id

    @visit('MANUFACTURER_SPECIFIC_GET')
    def handle_get(self, command: Command, context: Context):
        self.send_report(context)

    def send_report(self, context: Context):
        self.send_command(context, 'MANUFACTURER_SPECIFIC_REPORT',
                          manufacturer_id=self.manufacturer_id,
                          product_type_id=self.product_type_id,
                          product_id=self.product_id)
