from .request_manager import RequestManager
from .node_adding_controller import NodeAddingController
from .node_removing_controller import NodeRemovingController

from zwave.protocol.commands.add_node_to_network import AddNodeMode
from zwave.protocol.commands.remove_node_from_network import RemoveNodeMode
from zwave.protocol.commands.send_data import TransmitStatus

from tools import Object, log_warning, dump_hex

import random
from typing import Optional, List


class Network:
    def __init__(self, request_manager: RequestManager):
        self.request_manager = request_manager
        self.home_id = 0
        self.node_id = 1
        self.suc_id = self.node_id

        self.nodes = {}

        self.node_adding_controller = NodeAddingController(self)
        self.node_removing_controller = NodeRemovingController(self)

        self.reset()

    def reset(self):
        self.home_id = random.randint(0xC0000000, 0xFFFFFFFE)
        self.node_adding_controller.reset()
        self.node_removing_controller.reset()

    def set_suc_node_id(self, node_id: int) -> bool:
        return node_id == self.node_id

    async def assign_suc_return_route(self, node_id: int):
        yield TransmitStatus.OK

    def get_node_protocol_info(self, node_id: int) -> Optional[Object]:
        return self.nodes.get(node_id)

    def request_node_info(self, node_id: int):
        # Todo
        pass

    def add_node_to_network(self, mode: AddNodeMode):
        return self.node_adding_controller.add_node_to_network(mode)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        return self.node_removing_controller.remove_node_from_network(mode)

    async def send_data(self, node_id: int, data: List[int]):
        # Todo
        yield TransmitStatus.OK

        # if data == [0x5E, 0x01]:
        #     self.on_application_command(node_id, [0x5E, 0x02, 0x02, 0x05, 0x00, 0x07, 0x00, 0x07, 0x00])
        # elif data == [0x72, 0x04]:
        #     self.on_application_command(node_id, [0x72, 0x05, 0x00, 0x01, 0x00, 0x02, 0x00, 0x03])
        # elif data == [0x20, 0x02]:
        #     self.on_application_command(node_id, [0x20, 0x03, 0x00])

    def on_node_information_frame(self, node_id: Optional[int], node_info: Object):
        self.node_adding_controller.on_node_information_frame(node_id, node_info)
        self.node_removing_controller.on_node_information_frame(node_id, node_info)

    def on_application_command(self, node_id: int, data: List[int]):
        self.request_manager.send_request('APPLICATION_COMMAND_HANDLER',
                                          rx_status=0,
                                          rx_type=0,
                                          source_node=node_id,
                                          command=data)
