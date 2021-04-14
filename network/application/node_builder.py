from .node import Node
from .node_factory import NodeFactory
from .command_classes import command_class_factory

import humps


class NodeBuilder:
    def __init__(self, node_factory: NodeFactory):
        self.node_factory = node_factory

    def from_json(self, node_info: dict) -> Node:
        node = self.node_factory.create_node()
        node.__setstate__(node_info)

        for channel_info in node_info['channels']:
            channel = node.add_channel(channel_info['generic'], channel_info['specific'])

            for class_info in channel_info['commandClasses']:
                cls = command_class_factory.find_command_class(class_info['id'], class_info['version'])
                channel.add_command_class(cls, **humps.decamelize(class_info['args']))

        return node
