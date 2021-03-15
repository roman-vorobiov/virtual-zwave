from ..command_class import CommandClass
from ...node import Node
from zwave.protocol import Packet

from tools import visit


class ManufacturerSpecific(CommandClass):
    def __init__(
        self,
        node: Node,
        manufacturer_id: int,
        product_type_id: int,
        product_id: int
    ):
        super().__init__(node, 0x72, version=1)

        self.manufacturer_id = manufacturer_id
        self.product_type_id = product_type_id
        self.product_id = product_id

    @visit('MANUFACTURER_SPECIFIC_GET')
    def handle_get(self, command: Packet):
        self.send_report()

    def send_report(self):
        self.send_command('MANUFACTURER_SPECIFIC_REPORT',
                          manufacturer_id=self.manufacturer_id,
                          product_type_id=self.product_type_id,
                          product_id=self.product_id)
