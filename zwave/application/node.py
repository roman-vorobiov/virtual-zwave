from zwave.protocol import Packet

from tools import Object, log_warning

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zwave.core import Network


class Node:
    def __init__(self, network: 'Network', basic: int, generic: int, specific: int):
        self.network = network
        self.home_id: Optional[int] = None
        self.node_id: Optional[int] = None

        self.basic = basic
        self.generic = generic
        self.specific = specific

        self.command_classes = {}

    def add_to_network(self, home_id: int, node_id: int):
        self.node_id = node_id
        self.home_id = home_id

    def remove_from_network(self):
        self.node_id = None
        self.home_id = None

    def handle_command(self, command: Packet):
        if (command_class := self.command_classes.get(command.class_id)) is not None:
            command_class.handle_command(command)
        else:
            log_warning(f"Unhandled command: {command.class_id} {command.command_id}")

    def send_command(self, name: str, **kwargs):
        self.network.on_application_command(self.node_id, Packet(name, **kwargs))

    def send_node_information(self):
        node_info = Object(
            basic=self.basic,
            generic=self.generic,
            specific=self.specific,
            command_class_ids=list(self.command_classes.keys() - {0x20})
        )

        self.network.on_node_information_frame(self.node_id, node_info)
