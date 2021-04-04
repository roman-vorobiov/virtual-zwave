from .node_manager import NodeManager
from .controller_event_handler import ControllerEventHandler
from .command_handler import CommandHandler

from network.application import NodeFactory, ChannelFactory
from network.model.tinydb import DatabaseProvider
from network.client import Client
from network.protocol import CommandClassSerializer

from common import RemoteInterfaceImpl

from tools import load_yaml
from tools.websockets import RemoteConnection

import os


def make_command_class_serializer(*schema_paths: str) -> CommandClassSerializer:
    data = {}
    for schema_path in schema_paths:
        data.update(load_yaml(os.path.join("network", "protocol", schema_path)))

    return CommandClassSerializer(data)


class Core:
    def __init__(self, connection: RemoteConnection, client: Client):
        self.command_class_serializer = make_command_class_serializer("command_classes/management.yaml",
                                                                      "command_classes/transport_encapsulation.yaml",
                                                                      "command_classes/application.yaml")

        self.controller = RemoteInterfaceImpl(
            connection=connection
        )

        # Todo: let's pretend that RemoteInterface is not a service and isn't used in the data layer :)
        self.node_factory = NodeFactory(
            controller=self.controller
        )
        self.channel_factory = ChannelFactory(
            serializer=self.command_class_serializer
        )

        self.repository_provider = DatabaseProvider(
            node_factory=self.node_factory,
            channel_factory=self.channel_factory
        )
        self.nodes = self.repository_provider.get_nodes()

        self.node_manager = NodeManager(
            client=client,
            node_factory=self.node_factory,
            channel_factory=self.channel_factory,
            nodes=self.nodes
        )

        self.command_handler = CommandHandler(
            client=client,
            node_manager=self.node_manager
        )

        self.controller_event_handler = ControllerEventHandler(
            node_manager=self.node_manager
        )

    def process_command(self, command: str):
        self.command_handler.handle_command(command)

    def process_message(self, message: str):
        self.controller_event_handler.handle_message(message)
