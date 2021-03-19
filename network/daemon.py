from network.core import Core, UserInterface

from common import Daemon

from tools.websockets import NetworkClientConnection

import asyncio


class NetworkDaemon(Daemon):
    def __init__(self, port: int):
        self.user_interface = UserInterface()
        self.connection = NetworkClientConnection(port)
        self.handler = Core(self.connection)

    async def start(self):
        await self.connection.initialize()

        await asyncio.gather(self.handle_commands_from_user(),
                             self.handle_messages_from_network())

    def stop(self):
        self.user_interface.stop()
        asyncio.create_task(self.connection.close())

    async def handle_commands_from_user(self):
        async for command in self.user_interface.poll():
            self.handler.process_command(command)

    async def handle_messages_from_network(self):
        async for message in self.connection.poll():
            self.handler.process_message(message)
