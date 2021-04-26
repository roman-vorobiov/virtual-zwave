from network.application import Node, NodeFactory, NodeBuilder

from network.model import NodeRepository

from network.client import StateObserver

from typing import List


class NodeNotFoundException(Exception):
    def __init__(self, home_id: int, node_id: int):
        super().__init__()
        self.home_id = home_id
        self.node_id = node_id


class NodeManager:
    DEFAULT_HOME_ID = 0

    def __init__(self, state_observer: StateObserver, node_factory: NodeFactory, nodes: NodeRepository):
        self.state_observer = state_observer
        self.node_builder = NodeBuilder(node_factory)
        self.nodes = nodes

    def reset(self):
        self.nodes.clear()
        self.state_observer.on_network_reset()

    def get_nodes_as_json(self) -> List[dict]:
        return [node.to_json() for node in self.nodes.all()]

    def get_node(self, id: str) -> Node:
        return self.nodes.get(id)

    def find_node(self, home_id: int, node_id: int) -> Node:
        if (node := self.nodes.find(home_id, node_id)) is not None:
            return node

        raise NodeNotFoundException(home_id, node_id)

    def generate_new_node(self, node_info: dict) -> Node:
        node = self.node_builder.from_json(node_info)
        node.add_to_network(NodeManager.DEFAULT_HOME_ID, self.generate_node_id())
        self.nodes.add(node)

        self.state_observer.on_node_added(node)

        return node

    def remove_node(self, id: str):
        self.nodes.remove(id)
        self.state_observer.on_node_removed(id)

    def reset_node(self, id: str):
        node = self.get_node(id)
        node.reset(NodeManager.DEFAULT_HOME_ID, self.generate_node_id())
        self.state_observer.on_node_reset(node)

    def add_to_network(self, node: Node, home_id: int, node_id: int):
        node.add_to_network(home_id, node_id)
        self.state_observer.on_node_updated(node)

    def remove_from_network(self, node: Node):
        self.add_to_network(node, NodeManager.DEFAULT_HOME_ID, self.generate_node_id())

    def set_suc_node_id(self, home_id: int, node_id: int, suc_node_id: int):
        node = self.find_node(home_id, node_id)
        node.set_suc_node_id(suc_node_id)
        self.state_observer.on_node_updated(node)

    def generate_node_id(self) -> int:
        node_ids = (node.node_id for node in self.nodes.get_nodes_in_home(NodeManager.DEFAULT_HOME_ID))
        return max(node_ids, default=0) + 1
