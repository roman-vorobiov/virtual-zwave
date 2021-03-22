from .node_manager import NodeManager, NodeNotFoundException

from common import Network

from tools import log_error, log_info


class CommandHandler:
    def __init__(self, network: Network, node_manager: NodeManager):
        self.network = network
        self.node_manager = node_manager

    def handle_command(self, command: str):
        handlers = {
            'nif': self.send_nif,
            'generate': self.generate_node
        }

        command_name, *args = command.split(' ')
        try:
            handlers[command_name](*args)
        except NodeNotFoundException as e:
            log_error(f"Node not found: home ID = {e.home_id}, node ID = {e.node_id}")
        except (TypeError, ValueError):
            log_error("Invalid command")
        except KeyError:
            log_error("Unknown command")

    def send_nif(self, home_id: str, node_id: str):
        self.node_manager.get_node(int(home_id), int(node_id)).send_node_information()

    def generate_node(self):
        node = self.node_manager.generate_new_node()
        log_info(f"New node generated: home ID = {node.home_id}, node ID = {node.node_id}")
