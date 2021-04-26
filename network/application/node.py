from .channel import Channel
from .request_context import Context
from .utils import SecurityUtils, AssociationGroup

from network.client import Client
from network.protocol import CommandClassSerializer

from common import RemoteInterface, BaseNode, Model

from tools import Object, make_object

import humps
from typing import List, Optional


class Node(Model, BaseNode):
    def __init__(self, controller: RemoteInterface, client: Client, serializer: CommandClassSerializer):
        Model.__init__(self)
        BaseNode.__init__(self, controller)

        self.client = client
        self.serializer = serializer
        self.security_utils = SecurityUtils()

        self.home_id: Optional[int] = None
        self.node_id: Optional[int] = None
        self.suc_node_id: Optional[int] = None

        self.channels: List[Channel] = []

        self.secure = False

    def __getstate__(self):
        return {
            **Model.__getstate__(self),
            'home_id': self.home_id,
            'node_id': self.node_id,
            'suc_node_id': self.suc_node_id,
            'channels': self.channels,
            'network_key': (self.secure and self.security_utils.network_key) or None
        }

    def __setstate__(self, state: dict):
        self.node_id = state.get('node_id')
        self.home_id = state.get('home_id')
        self.suc_node_id = state.get('suc_node_id')

        if (network_key := state.get('network_key')) is not None:
            self.security_utils.set_network_key(network_key)
            self.secure = True

    def to_json(self):
        return humps.camelize(self.to_dict())

    def reset(self):
        self.node_id = None
        self.home_id = None
        self.suc_node_id = None
        self.secure = False
        self.security_utils.reset()

        for channel in self.channels:
            for cc in channel.command_classes.values():
                cc.reset_state()

    def add_channel(self, generic: int, specific: int, association_groups: List[AssociationGroup] = None) -> Channel:
        channel = Channel(self, generic, specific, association_groups or [])
        self.channels.append(channel)
        return channel

    def get_channel(self, channel_id: int):
        return self.channels[channel_id]

    @property
    def root_channel(self):
        return self.get_channel(0)

    def add_to_network(self, home_id: int, node_id: int):
        self.node_id = node_id
        self.home_id = home_id
        self.suc_node_id = None

    def set_suc_node_id(self, node_id: int):
        self.suc_node_id = node_id

    def handle_command(self, source_id: int, command: List[int]):
        self.send_message_in_current_network(source_id, 'ACK', {})

        self.root_channel.handle_command(command, Context(node_id=source_id))

    def get_node_info(self) -> Object:
        return make_object(
            generic=self.root_channel.generic,
            specific=self.root_channel.specific,
            command_class_ids=[cc.class_id for cc in self.root_channel.command_classes.values()
                               if cc.advertise_in_nif and cc.supported_non_securely]
        )

    def send_command(self, command: List[int], context: Context):
        if (queue := context.multi_cmd_response_queue) is not None:
            queue.append(command)
        elif context.secure:
            security_cc = self.root_channel.get_security_command_class()
            security_cc.send_encapsulated_command(context, command)
        else:
            self.send_message_in_current_network(context.node_id, 'APPLICATION_COMMAND', {
                'command': command
            })

    def send_node_information(self, home_id: int, node_id: int):
        self.send_message(home_id, node_id, 'APPLICATION_NODE_INFORMATION', {
            'nodeInfo': self.get_node_info().to_json()
        })

    def broadcast_node_information(self):
        self.broadcast_message('APPLICATION_NODE_INFORMATION', {
            'nodeInfo': self.get_node_info().to_json()
        })

    def notify_updated(self):
        self.client.send_message('NODE_UPDATED', {
            'node': humps.camelize(self.to_dict())
        })
