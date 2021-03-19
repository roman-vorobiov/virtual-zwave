from .network import Network as NetworkController

from common import Network

from tools import log_warning

import json


class NetworkEventHandler:
    def __init__(self, network: Network, network_controller: NetworkController):
        self.network = network
        self.network_controller = network_controller

    def process_message(self, message: str):
        command = json.loads(message)
        log_warning(command)

        # Todo
        self.network_controller.dummy_node.send_node_information()
