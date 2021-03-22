from network.application import Node, create_node

from common import Network

from typing import Dict


def make_dummy_node(network: Network) -> Node:
    return create_node(
        network,

        basic=0x04,
        generic=0x01,
        specific=0x01,

        manufacturer_id=1,
        product_type_id=2,
        product_id=3,

        role_type=0x05,
        installer_icon_type=0x0700,
        user_icon_type=0x0700
    )


class NodeNotFoundException(Exception):
    def __init__(self, home_id: int, node_id: int):
        super().__init__()
        self.home_id = home_id
        self.node_id = node_id


class NodeManager:
    DEFAULT_HOME_ID = 0

    def __init__(self, network: Network):
        self.network = network
        self.nodes: Dict[int, Dict[int, Node]] = {}

    def reset(self):
        self.nodes = {}

    def generate_new_node(self) -> Node:
        node = make_dummy_node(self.network)
        self.put_node_in_default_home(node)
        return node

    def add_node(self, home_id: int, node_id: int, node: Node):
        if node.home_id == NodeManager.DEFAULT_HOME_ID:
            del self.ensure_home(NodeManager.DEFAULT_HOME_ID)[node.node_id]

        node.add_to_network(home_id, node_id)
        self.ensure_home(home_id)[node_id] = node

    def remove_node(self, node: Node):
        del self.ensure_home(node.home_id)[node.node_id]
        node.remove_from_network()

        self.put_node_in_default_home(node)

    def put_node_in_default_home(self, node: Node):
        node_id = len(self.ensure_home(NodeManager.DEFAULT_HOME_ID)) + 1
        self.add_node(NodeManager.DEFAULT_HOME_ID, node_id, node)

    def get_node(self, home_id: int, node_id: int) -> Node:
        try:
            return self.nodes[home_id][node_id]
        except KeyError:
            raise NodeNotFoundException(home_id, node_id)

    def ensure_home(self, home_id: int):
        return self.nodes.setdefault(home_id, {})
