from zwave.core import ZwaveDevice, Core

from common import Daemon

from tools.websockets import NetworkServerConnection

import asyncio


class ZwaveDaemon(Daemon):
    def __init__(self, link: str, port: int):
        self.device = ZwaveDevice(link)
        self.connection = NetworkServerConnection(port)
        self.handler = Core(self.device, self.connection)

    async def start(self):
        self.device.initialize()
        await self.connection.initialize()

        await asyncio.gather(self.handle_packets_from_host(),
                             self.handle_messages_from_network())

    def stop(self):
        self.device.finalize()
        asyncio.create_task(self.connection.close())

    async def handle_packets_from_host(self):
        async for packet in self.device.poll():
            self.handler.process_packet(packet)

    async def handle_messages_from_network(self):
        async for message in self.connection.poll():
            self.handler.process_message(message)
