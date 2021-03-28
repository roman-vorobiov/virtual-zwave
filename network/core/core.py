from .node_manager import NodeManager
from .network_event_handler import NetworkEventHandler
from .command_handler import CommandHandler

from network.client import Client

from common import NetworkImpl

from tools.websockets import NetworkConnection


class Core:
    def __init__(self, connection: NetworkConnection, client: Client):
        self.network = NetworkImpl(
            connection=connection
        )

        self.node_manager = NodeManager(
            network=self.network,
            client=client
        )

        self.command_handler = CommandHandler(
            network=self.network,
            client=client,
            node_manager=self.node_manager
        )

        self.network_event_handler = NetworkEventHandler(
            node_manager=self.node_manager
        )

    def process_command(self, command: str):
        self.command_handler.handle_command(command)

    def process_message(self, message: str):
        self.network_event_handler.handle_message(message)
