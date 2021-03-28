from .node_manager import NodeManager
from .controller_event_handler import ControllerEventHandler
from .command_handler import CommandHandler

from network.client import Client

from common import RemoteInterfaceImpl

from tools.websockets import RemoteConnection


class Core:
    def __init__(self, connection: RemoteConnection, client: Client):
        self.controller = RemoteInterfaceImpl(
            connection=connection
        )

        self.node_manager = NodeManager(
            controller=self.controller,
            client=client
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
