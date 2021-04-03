from .command_classes import CommandClass
from .channel import Channel

from common import Command, RemoteInterface, BaseNode, Model

from tools import Object, make_object, serializable

from typing import List, Optional


@serializable(excluded_fields=['remote_interface', 'repository'])
class Node(Model, BaseNode):
    def __init__(self, controller: RemoteInterface, basic: int):
        Model.__init__(self)
        BaseNode.__init__(self, controller)

        self.home_id: Optional[int] = None
        self.node_id: Optional[int] = None
        self.suc_node_id: Optional[int] = None

        self.basic = basic

        self.channels: List[Channel] = []

    def add_channel(self, channel: Channel):
        self.channels.append(channel)

    def add_to_network(self, home_id: int, node_id: int):
        self.node_id = node_id
        self.home_id = home_id
        self.suc_node_id = None

    def set_suc_node_id(self, node_id: int):
        self.suc_node_id = node_id

    def handle_command(self, source_id: int, command: Command):
        self.channels[0].handle_command(source_id, command)

    def get_node_info(self) -> Object:
        command_classes = self.collect_command_classes()

        return make_object(
            basic=self.basic,
            generic=self.channels[0].generic,
            specific=self.channels[0].specific,
            command_class_ids=[cc.class_id for cc in command_classes if cc.class_id != 0x20],

            # Note: needed on the controller side to correctly deserialize commands
            command_class_versions={cc.class_id: cc.class_version for cc in command_classes}
        )

    def collect_command_classes(self) -> List[CommandClass]:
        all_command_classes = (command_class for channel in self.channels
                               for command_class in channel.command_classes.values())

        # set does not preserve order, but dict does
        return list(dict.fromkeys(all_command_classes))

    def send_command(self, destination_id: int, command: Command):
        self.send_message_in_current_network(destination_id, 'APPLICATION_COMMAND', {
            'classId': command.get_meta('class_id'),
            'classVersion': command.get_meta('class_version'),
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
