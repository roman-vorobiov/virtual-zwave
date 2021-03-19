from .network_event_handler import NetworkEventHandler
from .command_handler import CommandHandler

from common.network import Network

from tools.websockets import NetworkConnection


class Core:
    def __init__(self, connection: NetworkConnection):
        self.network = Network(
            connection=connection
        )

        self.command_handler = CommandHandler(
            network=self.network
        )

        self.network_event_handler = NetworkEventHandler(
            network=self.network
        )

    def process_command(self, command: str):
        self.command_handler.handle_command(command)

    def process_message(self, message: str):
        self.network_event_handler.handle_message(message)
