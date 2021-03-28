from .node_manager import NodeManager, NodeNotFoundException

from network.client import Client

from common import Network

from tools import log_error


class CommandHandler:
    def __init__(self, network: Network, client: Client, node_manager: NodeManager):
        self.network = network
        self.client = client
        self.node_manager = node_manager

    def handle_command(self, command: str):
        handlers = {
            'nif': self.send_nif,
            'generate': self.generate_node,
            'list': self.get_nodes
        }

        command_name, *args = command.split(' ')
        try:
            handlers.get(command_name, self.handle_unknown_command)(*args)
        except NodeNotFoundException as e:
            log_error(f"Node not found: home ID = {e.home_id}, node ID = {e.node_id}")
        except (TypeError, ValueError):
            log_error("Invalid command")

    def send_nif(self, home_id: str, node_id: str):
        self.node_manager.get_node(int(home_id), int(node_id)).broadcast_node_information()

    def generate_node(self):
        self.node_manager.generate_new_node()

    def get_nodes(self):
        self.client.send_message('NODES_LIST', {
            'nodes': list(self.node_manager.get_nodes())
        })

    def handle_unknown_command(self):
        log_error("Unknown command")
