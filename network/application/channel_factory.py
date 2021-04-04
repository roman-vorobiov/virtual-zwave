from .channel import Channel
from .node import Node

from network.protocol import CommandClassSerializer


class ChannelFactory:
    def __init__(self, serializer: CommandClassSerializer):
        self.serializer = serializer

    def create_channel(self, node: Node, generic: int, specific: int):
        channel = Channel(node, self.serializer, generic, specific)
        node.add_channel(channel)
        return channel
