from .command_classes import CommandClass

from common import Command, Network, BaseNode

from tools import Object, make_object, log_warning

import uuid
from typing import Dict


def generate_id() -> str:
    return str(uuid.uuid4())


class Node(BaseNode):
    def __init__(self, network: Network, basic: int, generic: int, specific: int):
        super().__init__(network)

        self.id = generate_id()
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

    def handle_command(self, source_id: int, command: Command):
        if (command_class := self.command_classes.get(command.get_meta('class_id'))) is not None:
            command_class.handle_command(source_id, command)
        else:
            log_warning(f"Node does not support command class {command.get_meta('class_id')}")

    def get_node_info(self) -> Object:
        return make_object(
            basic=self.basic,
            generic=self.generic,
            specific=self.specific,
            command_class_ids=list(self.command_classes.keys() - {0x20})
        )

    def send_command(self, destination_id: int, command: Command):
        self.send_message_in_current_network(destination_id, 'APPLICATION_COMMAND', {
            'classId': command.get_meta('class_id'),
            'command': command.get_meta('name'),
            'args': command.get_data()
        })

    def send_node_information(self, home_id: int, node_id: int):
        self.send_message(home_id, node_id, 'APPLICATION_NODE_INFORMATION', {
            'nodeInfo': self.get_node_info().to_json()
        })

    def broadcast_node_information(self):
        self.broadcast_message('APPLICATION_NODE_INFORMATION', {
            'nodeInfo': self.get_node_info().to_json()
        })
