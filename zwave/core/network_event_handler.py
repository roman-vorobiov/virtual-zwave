from .network_controller import NetworkController as NetworkController

from common import Network, NetworkMessageVisitor

from zwave.protocol import Packet

from tools import Object, visit

import json


class NetworkEventHandler(NetworkMessageVisitor):
    def __init__(self, network: Network, network_controller: NetworkController):
        self.network = network
        self.network_controller = network_controller

    def process_message(self, data: str):
        message = json.loads(data)
        self.visit(message)

    @visit('APPLICATION_COMMAND')
    def handle_application_command(self, message: dict):
        command = Packet(message['command'], **message['args'])
        self.network_controller.on_application_command(message['sourceNodeId'], command)

    @visit('APPLICATION_NODE_INFORMATION')
    def handle_node_information(self, message: dict):
        node_info = Object(**message['nodeInfo'])
        self.network_controller.on_node_information_frame(message['sourceNodeId'], node_info)
