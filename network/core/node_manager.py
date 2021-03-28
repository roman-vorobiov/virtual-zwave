from network.application import Node, create_node
from network.client import Client

from common import Network

from typing import Dict, Iterator


def make_dummy_node(network: Network) -> Node:
    return create_node(
        network,

        basic='BASIC_TYPE_ROUTING_SLAVE',
        generic='GENERIC_TYPE_SWITCH_BINARY',
        specific='SPECIFIC_TYPE_POWER_SWITCH_BINARY',

        manufacturer_id=1,
        product_type_id=2,
        product_id=3,

        zwave_plus_version=2,
        role_type='SLAVE_ALWAYS_ON',
        node_type='NODE_TYPE_ZWAVEPLUS_NODE',
        installer_icon_type='GENERIC_ON_OFF_POWER_SWITCH',
        user_icon_type='SPECIFIC_ON_OFF_POWER_SWITCH_PLUGIN'
    )


class NodeNotFoundException(Exception):
    def __init__(self, home_id: int, node_id: int):
        super().__init__()
        self.home_id = home_id
        self.node_id = node_id


class NodeManager:
    DEFAULT_HOME_ID = 0

    def __init__(self, network: Network, client: Client):
        self.network = network
        self.client = client
        self.nodes: Dict[int, Dict[int, Node]] = {}

    def reset(self):
        self.nodes = {}

    def get_nodes(self) -> Iterator[dict]:
        for home in self.nodes.values():
            for node in home.values():
                yield {
                    'id': node.id,
                    'homeId': node.home_id,
                    'nodeId': node.node_id,
                    'nodeInfo': node.get_node_info().to_json()
                }

    def generate_new_node(self) -> Node:
        node = make_dummy_node(self.network)
        self.put_node_in_default_home(node)
        return node

    def add_to_network(self, node: Node, home_id: int, node_id: int):
        if node.home_id == NodeManager.DEFAULT_HOME_ID:
            del self.ensure_home(NodeManager.DEFAULT_HOME_ID)[node.node_id]

        node.add_to_network(home_id, node_id)
        self.ensure_home(home_id)[node_id] = node

        self.notify_node_updated(node)

    def remove_from_network(self, node: Node):
        del self.ensure_home(node.home_id)[node.node_id]
        node.remove_from_network()

        self.put_node_in_default_home(node)

        self.notify_node_updated(node)

    def put_node_in_default_home(self, node: Node):
        node_id = len(self.ensure_home(NodeManager.DEFAULT_HOME_ID)) + 1
        self.add_to_network(node, NodeManager.DEFAULT_HOME_ID, node_id)

    def get_node(self, home_id: int, node_id: int) -> Node:
        try:
            return self.nodes[home_id][node_id]
        except KeyError:
            raise NodeNotFoundException(home_id, node_id)

    def ensure_home(self, home_id: int):
        return self.nodes.setdefault(home_id, {})

    def notify_node_updated(self, node: Node):
        self.client.send_message('NODE_UPDATED', {
            'id': node.id,
            'homeId': node.home_id,
            'nodeId': node.node_id,
            'nodeInfo': node.get_node_info().to_json()
        })
