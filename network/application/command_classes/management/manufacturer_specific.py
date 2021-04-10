from ..command_class import CommandClass, command_class
from ...channel import Channel

from network.protocol import Command

from tools import visit


@command_class('COMMAND_CLASS_MANUFACTURER_SPECIFIC', version=1)
class ManufacturerSpecific1(CommandClass):
    def __init__(
        self,
        channel: Channel,
        manufacturer_id: int,
        product_type_id: int,
        product_id: int
    ):
        super().__init__(channel)

        self.manufacturer_id = manufacturer_id
        self.product_type_id = product_type_id
        self.product_id = product_id

    @visit('MANUFACTURER_SPECIFIC_GET')
    def handle_get(self, command: Command):
        self.send_report()

    def send_report(self):
        self.send_command('MANUFACTURER_SPECIFIC_REPORT',
                          manufacturer_id=self.manufacturer_id,
                          product_type_id=self.product_type_id,
                          product_id=self.product_id)
