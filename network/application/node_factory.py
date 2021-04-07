from .node import Node

from network.client import Client
from network.protocol import CommandClassSerializer

from common import RemoteInterface


class NodeFactory:
    def __init__(self, controller: RemoteInterface, client: Client, serializer: CommandClassSerializer):
        self.controller = controller
        self.client = client
        self.serializer = serializer

    def create_node(self, basic: int) -> Node:
        return Node(self.controller, self.client, self.serializer, basic)
