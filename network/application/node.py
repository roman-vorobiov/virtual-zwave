from .command_classes import CommandClass
from .channel import Channel

from network.client import Client
from network.protocol import CommandClassSerializer

from common import RemoteInterface, BaseNode, Model

from tools import Object, make_object, Serializable

import humps
from dataclasses import dataclass, replace
from contextlib import contextmanager
from typing import List, Optional


@dataclass
class Context:
    node_id: int = 0
    endpoint: int = 0
    multi_cmd_response_queue: Optional[List[List[int]]] = None


class Node(Serializable, Model, BaseNode):
    def __init__(self, controller: RemoteInterface, client: Client, serializer: CommandClassSerializer, basic: int):
        Model.__init__(self)
        BaseNode.__init__(self, controller)

        self.client = client
        self.serializer = serializer

        self.home_id: Optional[int] = None
        self.node_id: Optional[int] = None
        self.suc_node_id: Optional[int] = None

        self.basic = basic

        self.channels: List[Channel] = []

        self.context = Context()

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['remote_interface']
        del state['client']
        del state['serializer']
        del state['repository']
        del state['context']
        return state

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

    def set_suc_node_id(self, node_id: int):
        self.suc_node_id = node_id

    def handle_command(self, source_id: int, command: List[int]):
        self.send_message_in_current_network(source_id, 'ACK', {})

        with self.update_context(node_id=source_id):
            self.channels[0].handle_command(command)

    def get_node_info(self) -> Object:
        command_classes = self.collect_command_classes()

        return make_object(
            basic=self.basic,
            generic=self.channels[0].generic,
            specific=self.channels[0].specific,
            command_class_ids=[cc.class_id for cc in command_classes if cc.class_id != 0x20]
        )

    def collect_command_classes(self) -> List[CommandClass]:
        all_command_classes = (command_class for channel in self.channels
                               for command_class in channel.command_classes.values())

        # set does not preserve order, but dict does
        return list(dict.fromkeys(all_command_classes))

    def send_command(self, command: List[int]):
        # Todo: associations
        destination_id = self.context.node_id or self.suc_node_id

        if (queue := self.context.multi_cmd_response_queue) is not None:
            queue.append(command)
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
