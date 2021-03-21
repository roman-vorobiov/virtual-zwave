from common import Network, NetworkMessageVisitor

from network.application import Node
from network.application.command_classes import make_command

from tools import visit

import json


class NetworkEventHandler(NetworkMessageVisitor):
    def __init__(self, network: Network, dummy_node: Node):
        self.network = network
        self.dummy_node = dummy_node

    def handle_message(self, data: str):
        message = json.loads(data)
        self.visit(message)

    @visit('ASSIGN_SUC_RETURN_ROUTE')
    def handle_assign_suc_return_route(self, message: dict):
        self.dummy_node.set_suc_node_id(message['sucNodeId'])

    @visit('REQUEST_NODE_INFO')
    def handle_request_node_info(self, message: dict):
        self.dummy_node.send_node_information(message['sourceNodeId'])

    @visit('APPLICATION_COMMAND')
    def handle_application_command(self, message: dict):
        command = make_command(message['classId'], message['command'], **message['args'])
        self.dummy_node.handle_command(message['sourceNodeId'], command)

    @visit('ADD_TO_NETWORK')
    def handle_add_to_network(self, message: dict):
        self.dummy_node.add_to_network(message['homeId'], message['newNodeId'])

    @visit('REMOVE_FROM_NETWORK')
    def handle_remove_from_network(self, message: dict):
        self.dummy_node.remove_from_network()
