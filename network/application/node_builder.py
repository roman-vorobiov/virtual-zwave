from .node import Node
from .node_factory import NodeFactory
from .channel import make_channel
from .command_classes.command_class import make_command_class

import humps


class NodeBuilder:
    def __init__(self, node_factory: NodeFactory):
        self.node_factory = node_factory

    def from_json(self, node_info: dict) -> Node:
        node = self.node_factory.create_node(basic=node_info['basic'])

        for channel_info in node_info['channels']:
            channel = make_channel(node, generic=channel_info['generic'], specific=channel_info['specific'])

            for class_info in channel_info['commandClasses']:
                make_command_class(
                    class_info['id'],
                    class_info['version'],
                    channel,
                    **humps.decamelize(class_info['args'])
                )

        return node
