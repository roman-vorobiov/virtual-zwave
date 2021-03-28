from network.core import Core
from network.client import Client

from common import Daemon

from tools.websockets import NetworkClientConnection

import asyncio


class NetworkDaemon(Daemon):
    def __init__(self, port: int):
        self.client = Client()
        self.connection = NetworkClientConnection(port)
        self.handler = Core(self.connection, self.client)

    async def start(self):
        await self.client.initialize()
        await self.connection.initialize()

        await asyncio.gather(self.handle_commands_from_user(),
                             self.handle_messages_from_network())

    def stop(self):
        asyncio.create_task(self.client.stop())
        asyncio.create_task(self.connection.close())

    async def handle_commands_from_user(self):
        async for command in self.client.poll():
            self.handler.process_command(command)

    async def handle_messages_from_network(self):
        async for message in self.connection.poll():
            self.handler.process_message(message)
