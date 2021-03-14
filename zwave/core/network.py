from .node_adding_controller import NodeAddingController

from zwave.protocol.commands.add_node_to_network import AddNodeMode
from zwave.protocol.commands.remove_node_from_network import RemoveNodeMode

from tools import Object

import random
from typing import Optional


class Network:
    def __init__(self):
        self.home_id = 0
        self.node_id = 1
        self.suc_id = self.node_id

        self.nodes = {}

        self.node_adding_controller = NodeAddingController(self)

        self.reset()

    def reset(self):
        self.home_id = random.randint(0xC0000000, 0xFFFFFFFE)
        self.node_adding_controller.reset()

    def set_suc_node_id(self, node_id: int) -> bool:
        return node_id == self.node_id

    def get_node_protocol_info(self, node_id: int) -> Optional[Object]:
        return self.nodes.get(node_id)

    def request_node_info(self, node_id: int):
        # Todo
        pass

    def add_node_to_network(self, mode: AddNodeMode):
        return self.node_adding_controller.add_node_to_network(mode)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        # Todo
        pass

    def on_node_information_frame(self, node_info: Object):
        self.node_adding_controller.on_node_information_frame(node_info)
