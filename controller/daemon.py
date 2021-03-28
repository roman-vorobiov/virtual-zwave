from controller.core import ControllerImpl, Core

from common import Daemon

from tools.websockets import RemoteServer

import asyncio


class ControllerDaemon(Daemon):
    def __init__(self, link: str, port: int):
        self.controller = ControllerImpl(link)
        self.network = RemoteServer(port)
        self.handler = Core(self.controller, self.network)

    async def start(self):
        self.controller.initialize()
        await self.network.initialize()

        await asyncio.gather(self.handle_packets_from_host(),
                             self.handle_messages_from_network())

    def stop(self):
        self.controller.finalize()
        asyncio.create_task(self.network.close())

    async def handle_packets_from_host(self):
        async for packet in self.controller.poll():
            self.handler.process_packet(packet)

    async def handle_messages_from_network(self):
        async for message in self.network.poll():
            self.handler.process_message(message)
