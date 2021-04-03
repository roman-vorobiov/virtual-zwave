from network.application import Node, NodeFactory, NodeBuilder

from network.model import NodeRepository

from network.client import Client

import humps
from typing import List


class NodeNotFoundException(Exception):
    def __init__(self, home_id: int, node_id: int):
        super().__init__()
        self.home_id = home_id
        self.node_id = node_id


class NodeManager:
    DEFAULT_HOME_ID = 0

    def __init__(self, client: Client, node_factory: NodeFactory, nodes: NodeRepository):
        self.client = client
        self.node_builder = NodeBuilder(node_factory)
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

    def generate_new_node(self, node_info: dict) -> Node:
        node = self.node_builder.from_json(node_info)
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
