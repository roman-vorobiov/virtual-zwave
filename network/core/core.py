from .node_manager import NodeManager
from .controller_event_handler import ControllerEventHandler
from .command_handler import CommandHandler

from network.application import NodeFactory

from network.model.tinydb import DatabaseProvider

from network.client import Client

from common import RemoteInterfaceImpl

from tools.websockets import RemoteConnection


class Core:
    def __init__(self, connection: RemoteConnection, client: Client):
        self.controller = RemoteInterfaceImpl(
            connection=connection
        )

        # Todo: let's pretend that RemoteInterface is not a service and isn't used in the data layer :)
        self.node_factory = NodeFactory(
            controller=self.controller
        )

        self.repository_provider = DatabaseProvider(
            node_factory=self.node_factory
        )
        self.nodes = self.repository_provider.get_nodes()

        self.node_manager = NodeManager(
            client=client,
            node_factory=self.node_factory,
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
