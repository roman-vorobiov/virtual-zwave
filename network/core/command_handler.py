from .node_manager import NodeManager

from network.client import Client

from common import RemoteMessageVisitor

from tools import visit, log_error

import json
import traceback


class CommandHandler(RemoteMessageVisitor):
    def __init__(self, client: Client, node_manager: NodeManager):
        self.client = client
        self.node_manager = node_manager

    def handle_command(self, data: str):
        message = json.loads(data)
        try:
            self.visit(message)
        except Exception:
            log_error(traceback.format_exc())

    @visit('GET_NODES')
    def handle_get_nodes(self, message: dict):
        self.client.send_message('NODES_LIST', {
            'nodes': self.node_manager.get_nodes_as_json()
        })

    @visit('CREATE_NODE')
    def handle_create_node(self, message: dict):
        self.node_manager.generate_new_node(message['node'])

    @visit('REMOVE_NODE')
    def handle_remove_node(self, message: dict):
        self.node_manager.remove_node(message['nodeId'])

    @visit('RESET_NETWORK')
    def handle_reset_network(self, message: dict):
        self.node_manager.reset()

    @visit('SEND_NIF')
    def handle_send_nif(self, message: dict):
        self.node_manager.get_node(message['nodeId']).broadcast_node_information()

    @visit('UPDATE_COMMAND_CLASS')
    def handle_update_node(self, message: dict):
        node = self.node_manager.get_node(message['nodeId'])
        channel = node.get_channel(message['channelId'])
        command_class = channel.get_command_class(message['classId'])
        command_class.update_state(**message['state'])

    @visit('RESET_NODE')
    def handle_reset_node(self, message: dict):
        self.node_manager.reset_node(message['nodeId'])
