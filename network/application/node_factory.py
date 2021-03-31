from .node import Node

from common import RemoteInterface


class NodeFactory:
    def __init__(self, controller: RemoteInterface):
        self.controller = controller

    def create_node(self, basic: int, generic: int, specific: int) -> Node:
        return Node(self.controller, basic, generic, specific)
