from network.application import Node

from common import Network

from tools import log_error


class CommandHandler:
    def __init__(self, network: Network, dummy_node: Node):
        self.network = network
        self.dummy_node = dummy_node

    def handle_command(self, command: str):
        handlers = {
            'nif': self.send_nif
        }

        handlers.get(command, self.handle_unknown_command)()

    def send_nif(self):
        # Todo: broadcast
        self.dummy_node.send_node_information(1)

    def handle_unknown_command(self):
        log_error("Unknown command")
