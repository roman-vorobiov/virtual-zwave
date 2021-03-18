from .core import Core

from tools import log_error
from tools.websockets import NetworkClientConnection

import asyncio
from aioconsole import ainput


class Daemon:
    def __init__(self, port: int):
        self.connection = NetworkClientConnection(port)
        self.handler = Core(self.connection)

    async def run(self):
        await self.connection.initialize()

        await asyncio.gather(self.handle_commands_from_user(),
                             self.handle_messages_from_network())

    async def stop(self):
        await self.connection.close()

    async def handle_commands_from_user(self):
        while True:
            command = await ainput()

            if command == 'stop':
                await self.stop()
                break
            elif command == 'send':
                await self.handler.send_test_data()
            else:
                log_error(f"Unknown command '{command}'")

    async def handle_messages_from_network(self):
        async for message in self.connection.poll():
            self.handler.process_message(message)
