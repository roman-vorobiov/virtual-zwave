from .node import Node

from network.client import Client

from common import RemoteInterface


class NodeFactory:
    def __init__(self, controller: RemoteInterface, client: Client):
        self.controller = controller
        self.client = client

    def create_node(self, basic: int) -> Node:
        return Node(self.controller, self.client, basic)
