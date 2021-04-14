from .channel import Channel
from .utils import SecurityUtils

from network.client import Client
from network.protocol import CommandClassSerializer

from common import RemoteInterface, BaseNode, Model

from tools import Object, make_object, Serializable

import humps
import asyncio
from dataclasses import dataclass, replace
from contextlib import contextmanager
from typing import List, Optional


@dataclass
class Context:
    node_id: int = 0
    endpoint: int = 0
    multi_cmd_response_queue: Optional[List[List[int]]] = None
    force_unsecure: bool = False


class Node(Serializable, Model, BaseNode):
    def __init__(self, controller: RemoteInterface, client: Client, serializer: CommandClassSerializer, secure=False):
        Model.__init__(self)
        BaseNode.__init__(self, controller)

        self.client = client
        self.serializer = serializer
        self.security_utils = SecurityUtils()

        self.home_id: Optional[int] = None
        self.node_id: Optional[int] = None
        self.suc_node_id: Optional[int] = None

        self.channels: List[Channel] = []

        self.context = Context()
        self.secure = secure

    def __getstate__(self):
        # Todo: save network key
        state = self.__dict__.copy()
        del state['remote_interface']
        del state['client']
        del state['serializer']
        del state['security_utils']
        del state['repository']
        del state['context']
        return state

    @property
    def lifeline(self):
        # Todo: associations
        return self.suc_node_id

    @contextmanager
    def update_context(self, **kwargs):
        new_context = replace(self.context, **kwargs)

        self.context, new_context = new_context, self.context
        try:
            yield
        finally:
            self.context, new_context = new_context, self.context

    def add_channel(self, generic: int, specific: int) -> Channel:
        channel = Channel(self, generic, specific)
        self.channels.append(channel)
        return channel

    def add_to_network(self, home_id: int, node_id: int):
        self.node_id = node_id
        self.home_id = home_id
        self.suc_node_id = None
        self.secure = False

    def set_suc_node_id(self, node_id: int):
        self.suc_node_id = node_id

    def handle_command(self, source_id: int, command: List[int]):
        self.send_message_in_current_network(source_id, 'ACK', {})

        with self.update_context(node_id=source_id):
            self.channels[0].handle_command(command)

    def get_node_info(self) -> Object:
        root_channel = self.channels[0]

        return make_object(
            generic=root_channel.generic,
            specific=root_channel.specific,
            command_class_ids=[cc.class_id for cc in root_channel.command_classes.values()
                               if cc.advertise_in_nif and not cc.secure]
        )

    def send_command(self, command: List[int]):
        destination_id = self.context.node_id or self.lifeline

        if (queue := self.context.multi_cmd_response_queue) is not None:
            queue.append(command)
        elif self.secure and not self.context.force_unsecure:
            security_cc = self.channels[0].get_security_command_class()
            asyncio.create_task(security_cc.send_encapsulated_command(command))
        else:
            self.send_message_in_current_network(destination_id, 'APPLICATION_COMMAND', {
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
