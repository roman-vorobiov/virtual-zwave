from .command_handler import CommandHandler

from common.network import Network

from tools.websockets import NetworkConnection


class Core:
    def __init__(self, connection: NetworkConnection):
        self.network = Network(connection)

        self.command_handler = CommandHandler(self.network)

    def process_message(self, message: str):
        self.command_handler.handle_message(message)

    # Todo
    async def send_test_data(self):
        await self.network.send_message({'args': "hello"})
