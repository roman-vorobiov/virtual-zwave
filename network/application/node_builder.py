from .node import Node
from .node_factory import NodeFactory
from .command_classes import SecurityLevel, command_class_factory
from .utils import AssociationGroup

import humps


class NodeBuilder:
    def __init__(self, node_factory: NodeFactory):
        self.node_factory = node_factory

    def from_json(self, node_info: dict) -> Node:
        return self.from_dict(humps.decamelize(node_info))

    def from_dict(self, node_info: dict) -> Node:
        node = self.node_factory.create_node()
        node.__setstate__(node_info)

        for channel_info in node_info['channels']:
            association_groups = [AssociationGroup(**group) for group in channel_info['association_groups']]
            channel = node.add_channel(channel_info['generic'], channel_info['specific'], association_groups)

            for class_info in channel_info['command_classes']:
                required_security = SecurityLevel(class_info.get('required_security', 'NONE'))
                cls = command_class_factory.find_command_class(class_info['class_id'], class_info['version'])
                channel.add_command_class(cls, required_security, **class_info.get('state', {}))

        return node
