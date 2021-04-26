from .node import Node

from network.client import StateObserver
from network.protocol import CommandClassSerializer

from common import RemoteInterface


class NodeFactory:
    def __init__(self, controller: RemoteInterface, state_observer: StateObserver, serializer: CommandClassSerializer):
        self.controller = controller
        self.state_observer = state_observer
        self.serializer = serializer

    def create_node(self) -> Node:
        return Node(self.controller, self.state_observer, self.serializer)
