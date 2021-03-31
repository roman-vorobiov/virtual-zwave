from .remote_interface import RemoteInterface

from typing import Optional


class BaseNode:
    def __init__(self, remote_interface: RemoteInterface):
        self.remote_interface = remote_interface

    def send_message_in_current_network(self, node_id: int, message_type: str, details: dict):
        self.send_message(self.home_id, node_id, message_type, details)

    def send_message(self, home_id: int, node_id: int, message_type: str, details: dict):
        self.broadcast_message(message_type, {
            **details,
            'destination': {
                'homeId': home_id,
                'nodeId': node_id
            }
        })

    def broadcast_message(self, message_type: str, details: dict):
        self.remote_interface.send_message({
            'messageType': message_type,
            'message': {
                **details,
                'source': {
                    'homeId': self.home_id,
                    'nodeId': self.node_id
                }
            }
        })
