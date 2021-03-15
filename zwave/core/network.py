from .request_manager import RequestManager
from .node_adding_controller import NodeAddingController
from .node_removing_controller import NodeRemovingController

from zwave.protocol import Packet
from zwave.protocol.commands.add_node_to_network import AddNodeMode
from zwave.protocol.commands.remove_node_from_network import RemoveNodeMode
from zwave.protocol.commands.send_data import TransmitStatus
from zwave.protocol.serialization import CommandClassSerializer

from zwave.application import create_node

from tools import Object, log_warning, dump_hex

import random
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from zwave.application import Node


def make_dummy_node(network: 'Network') -> 'Node':
    return create_node(
        network,

        basic=0x04,
        generic=0x01,
        specific=0x01,

        manufacturer_id=0x0001,
        product_type_id=0x0002,
        product_id=0x0003,

        role_type=0x05,
        installer_icon_type=0x0700,
        user_icon_type=0x0700
    )


class Network:
    def __init__(self, command_class_serializer: CommandClassSerializer, request_manager: RequestManager):
        self.command_class_serializer = command_class_serializer
        self.request_manager = request_manager
        self.home_id = 0
        self.node_id = 1
        self.suc_id = self.node_id

        self.nodes = {}
        self.dummy_node = make_dummy_node(self)

        self.node_adding_controller = NodeAddingController(self)
        self.node_removing_controller = NodeRemovingController(self)

        self.reset()

    def reset(self):
        self.home_id = random.randint(0xC0000000, 0xFFFFFFFE)
        self.nodes = {}
        self.node_adding_controller.reset()
        self.node_removing_controller.reset()

    def set_suc_node_id(self, node_id: int) -> bool:
        return node_id == self.node_id

    async def assign_suc_return_route(self, node_id: int):
        yield TransmitStatus.OK

    def get_node_protocol_info(self, node_id: int) -> Optional[Object]:
        return self.nodes.get(node_id)

    def request_node_info(self, node_id: int):
        self.dummy_node.send_node_information()

    def add_node_to_network(self, mode: AddNodeMode):
        return self.node_adding_controller.add_node_to_network(mode)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        return self.node_removing_controller.remove_node_from_network(mode)

    async def send_data(self, node_id: int, data: List[int]):
        command = self.command_class_serializer.from_bytes(data)
        log_warning(f"{node_id} < {command.name} {command.fields}")
        yield TransmitStatus.OK
        self.dummy_node.handle_command(command)

    def on_node_information_frame(self, node_id: Optional[int], node_info: Object):
        self.node_adding_controller.on_node_information_frame(node_id, node_info)
        self.node_removing_controller.on_node_information_frame(node_id, node_info)

    def on_application_command(self, node_id: int, command: Packet):
        log_warning(f"{node_id} > {command.name} {command.fields}")
        data = self.command_class_serializer.to_bytes(command)
        self.request_manager.send_request('APPLICATION_COMMAND_HANDLER',
                                          rx_status=0,
                                          rx_type=0,
                                          source_node=node_id,
                                          command=data)
