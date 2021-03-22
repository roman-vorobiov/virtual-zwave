from .network_controller import NetworkController as NetworkController
from .request_manager import RequestManager

from common import Network, NetworkMessageVisitor

from zwave.protocol import Packet
from zwave.protocol.commands.application_slave_update import UpdateStatus

from tools import Object, visit

import json


class NetworkEventHandler(NetworkMessageVisitor):
    def __init__(self, network: Network, network_controller: NetworkController, request_manager: RequestManager):
        self.network = network
        self.network_controller = network_controller
        self.request_manager = request_manager

    def process_message(self, data: str):
        message = json.loads(data)
        self.visit(message)

    @visit('APPLICATION_COMMAND')
    def handle_application_command(self, message: dict):
        command = Packet(message['command'], **message['args'])
        self.network_controller.on_application_command(message['source']['nodeId'], command)

    @visit('APPLICATION_NODE_INFORMATION')
    def handle_node_information(self, message: dict):
        node_info = Object(
            basic=message['nodeInfo']['basic'],
            generic=message['nodeInfo']['generic'],
            specific=message['nodeInfo']['specific'],
            command_class_ids=message['nodeInfo']['commandClassIds']
        )

        home_id = message['source']['homeId']
        node_id = message['source']['nodeId']

        if 'destination' not in message:
            # Broadcast
            self.network_controller.on_node_information_frame(home_id, node_id, node_info)
        else:
            self.request_manager.send_request('APPLICATION_SLAVE_UPDATE',
                                              status=UpdateStatus.NODE_INFO_RECEIVED,
                                              node_id=node_id,
                                              node_info=node_info)
