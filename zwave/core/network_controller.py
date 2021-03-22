from .request_manager import RequestManager
from .node_adding_controller import NodeAddingController
from .node_removing_controller import NodeRemovingController

from common import Network

from zwave.protocol import Packet
from zwave.protocol.commands.add_node_to_network import AddNodeMode
from zwave.protocol.commands.remove_node_from_network import RemoveNodeMode
from zwave.protocol.commands.send_data import TransmitStatus
from zwave.protocol.serialization import CommandClassSerializer

from tools import Object

import random
from typing import Optional, List


def generate_new_home_id() -> int:
    return random.randint(0xC0000000, 0xFFFFFFFE)


class NetworkController:
    def __init__(
        self,
        command_class_serializer: CommandClassSerializer,
        request_manager: RequestManager,
        network: Network
    ):
        self.command_class_serializer = command_class_serializer
        self.request_manager = request_manager
        self.network = network

        self.node_adding_controller = NodeAddingController(self)
        self.node_removing_controller = NodeRemovingController(self)

        self.home_id = generate_new_home_id()
        self.node_id = 1
        self.suc_id = self.node_id

        self.nodes = {}

    def reset(self):
        self.home_id = generate_new_home_id()
        self.nodes = {}

    @classmethod
    def generate_new_home_id(cls) -> int:
        return random.randint(0xC0000000, 0xFFFFFFFE)

    def set_suc_node_id(self, node_id: int) -> bool:
        return node_id == self.node_id

    async def assign_suc_return_route(self, node_id: int):
        self.send_message_in_current_network(node_id, 'ASSIGN_SUC_RETURN_ROUTE', {
            'sucNodeId': self.suc_id
        })
        yield TransmitStatus.OK

    def get_node_protocol_info(self, node_id: int) -> Optional[Object]:
        return self.nodes.get(node_id)

    def request_node_info(self, node_id: int):
        self.send_message_in_current_network(node_id, 'REQUEST_NODE_INFO', {})

    def add_node_to_network(self, mode: AddNodeMode):
        return self.node_adding_controller.add_node_to_network(mode)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        return self.node_removing_controller.remove_node_from_network(mode)

    async def send_data(self, destination_node_id: int, data: List[int]):
        command = self.command_class_serializer.from_bytes(data)

        self.send_message_in_current_network(destination_node_id, 'APPLICATION_COMMAND', {
            'classId': command.class_id,
            'command': command.name,
            'args': command.fields
        })

        yield TransmitStatus.OK

    def on_node_information_frame(self, home_id: int, node_id: int, node_info: Object):
        self.node_adding_controller.on_node_information_frame(home_id, node_id, node_info)
        self.node_removing_controller.on_node_information_frame(home_id, node_id, node_info)

    def on_application_command(self, node_id: int, command: Packet):
        data = self.command_class_serializer.to_bytes(command)
        self.request_manager.send_request('APPLICATION_COMMAND_HANDLER',
                                          rx_status=0,
                                          rx_type=0,
                                          source_node=node_id,
                                          command=data)

    def send_message_in_current_network(self, node_id: int, message_type: str, details: dict):
        self.send_message(self.home_id, node_id, message_type, details)

    def send_message(self, home_id: int, node_id: int, message_type: str, details: dict):
        self.broadcast_message(message_type, {
            **details,
            'destination': {
                'homeId': home_id,
                'nodeId': node_id
            }
        })

    def broadcast_message(self, message_type: str, details: dict):
        self.network.send_message({
            'messageType': message_type,
            'message': {
                **details,
                'source': {
                    'homeId': self.home_id,
                    'nodeId': self.node_id
                }
            }
        })
