from .network_controller import NetworkController as NetworkController
from .request_manager import RequestManager

from common import RemoteMessageVisitor

from controller.protocol.commands.application_slave_update import UpdateStatus

from tools import Object, visit

import json


class NetworkEventHandler(RemoteMessageVisitor):
    def __init__(self, network_controller: NetworkController, request_manager: RequestManager):
        self.network_controller = network_controller
        self.request_manager = request_manager

    def process_message(self, data: str):
        message = json.loads(data)
        self.visit(message)

    @visit('ACK')
    def handle_ack(self, message: dict):
        self.network_controller.on_ack(message['source']['nodeId'])

    @visit('APPLICATION_COMMAND')
    def handle_application_command(self, message: dict):
        if message['destination']['nodeId'] == self.network_controller.node_id:
            self.network_controller.on_application_command(message['source']['nodeId'], message['command'])
        else:
            # Todo: Messages should go to the destination directly w/o going through the controller
            self.network_controller.remote_interface.send_message({
                'messageType': 'APPLICATION_COMMAND',
                'message': message
            })

    @visit('APPLICATION_NODE_INFORMATION')
    def handle_node_information(self, message: dict):
        node_info = Object.from_json(message['nodeInfo'])

        # Todo: support controller nodes
        node_info.basic = 0x04

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
