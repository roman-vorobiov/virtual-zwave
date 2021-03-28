from network.core import Core
from network.client import Client

from common import Daemon

from tools.websockets import RemoteClient

import asyncio


class NetworkDaemon(Daemon):
    def __init__(self, port: int):
        self.client = Client()
        self.controller = RemoteClient(port)
        self.handler = Core(self.controller, self.client)

    async def start(self):
        await self.client.initialize()
        await self.controller.initialize()

        await asyncio.gather(self.handle_commands_from_user(),
                             self.handle_messages_from_network())

    def stop(self):
        asyncio.create_task(self.client.stop())
        asyncio.create_task(self.controller.close())

    async def handle_commands_from_user(self):
        async for command in self.client.poll():
            self.handler.process_command(command)

    async def handle_messages_from_network(self):
        async for message in self.controller.poll():
            self.handler.process_message(message)
