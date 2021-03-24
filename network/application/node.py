from .command_classes import CommandClass

from zwave.protocol import Packet

from common import Network

from tools import Object, log_warning

from typing import Optional, Dict


class Node:
    def __init__(self, network: Network, basic: int, generic: int, specific: int):
        self.network = network

        self.home_id: Optional[int] = None
        self.node_id: Optional[int] = None
        self.suc_node_id: Optional[int] = None

        self.basic = basic
        self.generic = generic
        self.specific = specific

        self.command_classes: Dict[int, CommandClass] = {}

    def add_command_class(self, cc: CommandClass):
        self.command_classes[cc.class_id] = cc

    def add_to_network(self, home_id: int, node_id: int):
        self.node_id = node_id
        self.home_id = home_id

    def remove_from_network(self):
        self.node_id = None
        self.home_id = None
        self.suc_node_id = None

    def set_suc_node_id(self, node_id: int):
        self.suc_node_id = node_id

    def handle_command(self, source_id: int, command: Packet):
        if (command_class := self.command_classes.get(command.class_id)) is not None:
            command_class.handle_command(source_id, command)
        else:
            log_warning(f"Unhandled command class: {command.class_id} {command.name}")

    def get_node_info(self) -> Object:
        return Object(
            basic=self.basic,
            generic=self.generic,
            specific=self.specific,
            # Todo: names instead of IDs
            command_class_ids=list(self.command_classes.keys() - {0x20})
        )

    def send_command(self, destination_id: int, command: Packet):
        self.send_message_in_current_network(destination_id, 'APPLICATION_COMMAND', {
            'classId': command.class_id,
            'command': command.name,
            'args': command.fields
        })

    def send_node_information(self, home_id: Optional[int] = None, node_id: Optional[int] = None):
        node_info = self.get_node_info().to_json()

        if home_id is not None and node_id is not None:
            self.send_message(home_id, node_id, 'APPLICATION_NODE_INFORMATION', {
                'nodeInfo': node_info
            })
        else:
            self.broadcast_message('APPLICATION_NODE_INFORMATION', {
                'nodeInfo': node_info
            })

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
        self.network.send_message({
            'messageType': message_type,
            'message': {
                **details,
                'source': {
                    'homeId': self.home_id,
                    'nodeId': self.node_id
                }
            }
        })
