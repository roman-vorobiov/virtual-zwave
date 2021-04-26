from .client import Client

import humps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from network.application.node import Node
    from network.application.channel import Channel
    from network.application.command_classes import CommandClass


class StateObserver:
    def __init__(self, client: Client):
        self.client = client

    def on_node_added(self, node: 'Node'):
        data = node.to_dict()

        self.client.send_message('NODE_ADDED', {
            'node': humps.camelize(data)
        })

    def on_node_removed(self, id: str):
        self.client.send_message('NODE_REMOVED', {
            'nodeId': id
        })

    def on_network_reset(self):
        # Todo: maybe individual 'NODE_REMOVED' messages are better?
        self.client.send_message('NODES_LIST', {
            'nodes': []
        })

    def on_node_reset(self, node: 'Node'):
        data = node.to_dict()

        self.client.send_message('NODE_RESET', {
            'node': humps.camelize(data)
        })

    def on_node_updated(self, node: 'Node'):
        data = node.to_dict()
        del data['channels']

        self.client.send_message('NODE_UPDATED', {
            'node': humps.camelize(data)
        })

    def on_channel_updated(self, channel: 'Channel'):
        data = channel.to_dict()
        del data['command_classes']

        self.client.send_message('CHANNEL_UPDATED', {
            'nodeId': channel.node.id,
            'channel': humps.camelize(data)
        })

    def on_command_class_updated(self, command_class: 'CommandClass'):
        data = command_class.to_dict()

        self.client.send_message('COMMAND_CLASS_UPDATED', {
            'nodeId': command_class.node.id,
            'channelId': command_class.channel.endpoint,
            'commandClass': humps.camelize(data)
        })
