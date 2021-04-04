from .node_manager import NodeManager, NodeNotFoundException

from network.application import Node

from common import RemoteMessageVisitor

from tools import visit, log_error

import json


class ControllerEventHandler(RemoteMessageVisitor):
    def __init__(self, node_manager: NodeManager):
        self.node_manager = node_manager

    def handle_message(self, data: str):
        message = json.loads(data)
        try:
            self.visit(message)
        except NodeNotFoundException as e:
            log_error(f"Node not found: home ID = {e.home_id}, node ID = {e.node_id}")

    @visit('ACK')
    def handle_ack(self, message: dict):
        pass

    @visit('ASSIGN_SUC_RETURN_ROUTE')
    def handle_assign_suc_return_route(self, message: dict):
        home_id = message['destination']['homeId']
        node_id = message['destination']['nodeId']
        suc_node_id = message['sucNodeId']

        self.node_manager.set_suc_node_id(home_id, node_id, suc_node_id)

    @visit('REQUEST_NODE_INFO')
    def handle_request_node_info(self, message: dict):
        home_id = message['source']['homeId']
        node_id = message['source']['nodeId']
        self.get_node(message).send_node_information(home_id, node_id)

    @visit('APPLICATION_COMMAND')
    def handle_application_command(self, message: dict):
        node = self.get_node(message)
        node.handle_command(message['source']['nodeId'], message['command'])

    @visit('ADD_TO_NETWORK')
    def handle_add_to_network(self, message: dict):
        node = self.get_node(message)
        self.node_manager.add_to_network(node, message['source']['homeId'], message['newNodeId'])

    @visit('REMOVE_FROM_NETWORK')
    def handle_remove_from_network(self, message: dict):
        node = self.get_node(message)
        self.node_manager.remove_from_network(node)

    @visit('ADD_NODE_STARTED', 'REMOVE_NODE_STARTED')
    def handle_transfer_presentation(self, message: dict):
        pass

    def get_node(self, message: dict) -> Node:
        home_id = message['destination']['homeId']
        node_id = message['destination']['nodeId']

        return self.node_manager.find_node(home_id, node_id)
