from .channel import Channel
from .request_context import Context
from .utils import SecurityUtils, AssociationGroup

from network.client import Client
from network.protocol import CommandClassSerializer

from common import RemoteInterface, BaseNode, Model

from tools import Object, make_object, Serializable

import humps
from typing import List, Optional


class Node(Serializable, Model, BaseNode):
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
        state = self.__dict__.copy()
        state['network_key'] = self.security_utils.network_key
        del state['remote_interface']
        del state['client']
        del state['serializer']
        del state['security_utils']
        del state['repository']
        return state

    def __setstate__(self, state: dict):
        if (network_key := state.get('network_key')) is not None:
            self.security_utils.set_network_key(network_key)

        self.node_id = state.get('node_id')
        self.home_id = state.get('home_id')
        self.suc_node_id = state.get('suc_node_id')

        self.secure = state.get('secure', False)

    def to_json(self):
        return humps.camelize(self.to_dict())

    def add_channel(self, generic: int, specific: int, association_groups: List[AssociationGroup] = None) -> Channel:
        channel = Channel(self, generic, specific, association_groups or [])
        self.channels.append(channel)
        return channel

    def add_to_network(self, home_id: int, node_id: int):
        self.node_id = node_id
        self.home_id = home_id
        self.suc_node_id = None
        self.secure = False
        self.security_utils.reset()

        for channel in self.channels:
            for cc in channel.command_classes.values():
                cc.reset_state()

    def set_suc_node_id(self, node_id: int):
        self.suc_node_id = node_id

    def handle_command(self, source_id: int, command: List[int]):
        self.send_message_in_current_network(source_id, 'ACK', {})

        self.channels[0].handle_command(command, Context(node_id=source_id))

    def get_node_info(self) -> Object:
        root_channel = self.channels[0]

        return make_object(
            generic=root_channel.generic,
            specific=root_channel.specific,
            command_class_ids=[cc.class_id for cc in root_channel.command_classes.values()
                               if cc.advertise_in_nif and cc.supported_non_securely]
        )

    def send_command(self, command: List[int], context: Context):
        if (queue := context.multi_cmd_response_queue) is not None:
            queue.append(command)
        elif context.secure:
            security_cc = self.channels[0].get_security_command_class()
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
