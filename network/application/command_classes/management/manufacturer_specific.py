from ..command_class import CommandClass, command_class
from ...node import Node
from zwave.protocol import Packet

from tools import visit


@command_class('COMMAND_CLASS_MANUFACTURER_SPECIFIC')
class ManufacturerSpecific(CommandClass):
    def __init__(
        self,
        node: Node,
        manufacturer_id: int,
        product_type_id: int,
        product_id: int
    ):
        super().__init__(node)

        self.manufacturer_id = manufacturer_id
        self.product_type_id = product_type_id
        self.product_id = product_id

    @visit('MANUFACTURER_SPECIFIC_GET')
    def handle_get(self, command: Packet, source_id: int):
        self.send_report(destination_id=source_id)

    def send_report(self, destination_id: int):
        command = self.make_command('MANUFACTURER_SPECIFIC_REPORT',
                                    manufacturer_id=self.manufacturer_id,
                                    product_type_id=self.product_type_id,
                                    product_id=self.product_id)

        self.send_command(destination_id, command)
