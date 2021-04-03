from network.application import Node, NodeFactory, Channel
from network.application.command_classes import command_class_factory

from network.model import NodeRepository

from network.client import Client

import humps
from typing import List


def make_dummy_node(node_factory: NodeFactory) -> Node:
    node = node_factory.create_node(basic=0x04)

    channel = Channel(node, generic=0x10, specific=0x01)
    node.add_channel(channel)

    # COMMAND_CLASS_MANUFACTURER_SPECIFIC
    command_class_factory.create_command_class(
        0x72,
        1,
        channel,
        manufacturer_id=1,
        product_type_id=2,
        product_id=3
    )

    # COMMAND_CLASS_ZWAVEPLUS_INFO
    command_class_factory.create_command_class(
        0x5E,
        2,
        channel,
        zwave_plus_version=2,
        role_type=0x05,
        node_type=0x00,
        installer_icon_type=0x0700,
        user_icon_type=0x0701
    )

    # COMMAND_CLASS_VERSION
    command_class_factory.create_command_class(
        0x86,
        1,
        channel,
        protocol_library_type=0x06,
        protocol_version=(1, 0),
        application_version=(1, 0)
    )

    # COMMAND_CLASS_BASIC
    command_class_factory.create_command_class(
        0x20,
        1,
        channel
    )

    return node


class NodeNotFoundException(Exception):
    def __init__(self, home_id: int, node_id: int):
        super().__init__()
        self.home_id = home_id
        self.node_id = node_id


class NodeManager:
    DEFAULT_HOME_ID = 0

    def __init__(self, client: Client, node_factory: NodeFactory, nodes: NodeRepository):
        self.client = client
        self.node_factory = node_factory
        self.nodes = nodes

    def reset(self):
        self.nodes.clear()

    def get_nodes_as_json(self) -> List[dict]:
        return humps.camelize(self.nodes.all())

    def get_node(self, id: str) -> Node:
        return self.nodes.get(id)

    def find_node(self, home_id: int, node_id: int) -> Node:
        if (node := self.nodes.find(home_id, node_id)) is not None:
            return node

        raise NodeNotFoundException(home_id, node_id)

    def generate_new_node(self) -> Node:
        node = make_dummy_node(self.node_factory)
        self.nodes.add(node)
        self.put_node_in_default_home(node)
        return node

    def add_to_network(self, node: Node, home_id: int, node_id: int):
        node.add_to_network(home_id, node_id)
        node.save()
        self.notify_node_updated(node)

    def remove_from_network(self, node: Node):
        self.put_node_in_default_home(node)

    def set_suc_node_id(self, home_id: int, node_id: int, suc_node_id: int):
        node = self.find_node(home_id, node_id)
        node.set_suc_node_id(suc_node_id)
        node.save()
        self.notify_node_updated(node)

    def put_node_in_default_home(self, node: Node):
        self.add_to_network(node, NodeManager.DEFAULT_HOME_ID, self.generate_node_id())

    def generate_node_id(self) -> int:
        return max(self.nodes.get_node_ids(NodeManager.DEFAULT_HOME_ID), default=0) + 1

    def notify_node_updated(self, node: Node):
        self.client.send_message('NODE_UPDATED', humps.camelize(node.to_dict()))
