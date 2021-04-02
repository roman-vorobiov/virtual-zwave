from .request_manager import RequestManager
from .node_adding_controller import NodeAddingController
from .node_removing_controller import NodeRemovingController

from controller.model import State, NodeInfoRepository

from controller.protocol.commands.add_node_to_network import AddNodeMode
from controller.protocol.commands.remove_node_from_network import RemoveNodeMode
from controller.protocol.commands.send_data import TransmitStatus
from controller.protocol.serialization import CommandClassSerializer

from common import Command, RemoteInterface, BaseNode

from tools import Object

import random
from typing import Optional, List


class NetworkController(BaseNode):
    def __init__(
        self,
        command_class_serializer: CommandClassSerializer,
        state: State,
        node_infos: NodeInfoRepository,
        request_manager: RequestManager,
        network: RemoteInterface
    ):
        super().__init__(network)

        self.command_class_serializer = command_class_serializer
        self.state = state
        self.node_infos = node_infos
        self.request_manager = request_manager

        self.node_adding_controller = NodeAddingController(self)
        self.node_removing_controller = NodeRemovingController(self)

        self.restore()

    @property
    def home_id(self) -> int:
        return self.state.get('home_id')

    @home_id.setter
    def home_id(self, value: int):
        self.state.set('home_id', value)

    @property
    def node_id(self):
        return self.state.get('node_id')

    @node_id.setter
    def node_id(self, value: int):
        self.state.set('node_id', value)

    @property
    def suc_node_id(self):
        return self.state.get('suc_node_id')

    @suc_node_id.setter
    def suc_node_id(self, value: int):
        self.state.set('suc_node_id', value)

    def restore(self):
        if self.state.empty():
            self.reset()

    def reset(self):
        self.home_id = self.generate_new_home_id()
        self.node_id = 1
        self.suc_node_id = self.node_id

        self.node_infos.clear()

    @classmethod
    def generate_new_home_id(cls) -> int:
        return random.randint(0xC0000000, 0xFFFFFFFE)

    def set_suc_node_id(self, node_id: int) -> bool:
        return node_id == self.node_id

    async def assign_suc_return_route(self, node_id: int):
        self.send_message_in_current_network(node_id, 'ASSIGN_SUC_RETURN_ROUTE', {
            'sucNodeId': self.suc_node_id
        })
        yield TransmitStatus.OK

    def get_node_protocol_info(self, node_id: int) -> Optional[Object]:
        return self.node_infos.find(node_id)

    def request_node_info(self, node_id: int):
        self.send_message_in_current_network(node_id, 'REQUEST_NODE_INFO', {})

    def add_node_to_network(self, mode: AddNodeMode):
        return self.node_adding_controller.add_node_to_network(mode)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        return self.node_removing_controller.remove_node_from_network(mode)

    async def send_data(self, destination_node_id: int, data: List[int]):
        node_info = self.node_infos.find(destination_node_id)
        class_versions = {int(class_id): version for class_id, version in node_info.command_class_versions.items()}
        command = self.command_class_serializer.from_bytes(data, class_versions)

        self.send_message_in_current_network(destination_node_id, 'APPLICATION_COMMAND', {
            'classId': command.get_meta('class_id'),
            'command': command.get_meta('name'),
            'args': command.get_data()
        })

        yield TransmitStatus.OK

    def on_node_information_frame(self, home_id: int, node_id: int, node_info: Object):
        self.node_adding_controller.on_node_information_frame(home_id, node_id, node_info)
        self.node_removing_controller.on_node_information_frame(home_id, node_id, node_info)

    def on_application_command(self, node_id: int, command: Command):
        data = self.command_class_serializer.to_bytes(command)
        self.request_manager.send_request('APPLICATION_COMMAND_HANDLER',
                                          rx_status=0,
                                          rx_type=0,
                                          source_node=node_id,
                                          command=data)
