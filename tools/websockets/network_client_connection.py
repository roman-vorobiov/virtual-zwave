from .network_connection import NetworkConnection

from tools import log_info, log_error

import websockets
import asyncio


class NetworkClientConnection(NetworkConnection):
    def __init__(self, port: int):
        super().__init__()
        self.uri = f"ws://localhost:{port}"

    async def initialize(self):
        super().initialize()
        await self.ensure_connection()

    async def connect(self) -> bool:
        try:
            self.websocket = await websockets.connect(self.uri)
            asyncio.create_task(self.start_polling())

            log_info(f"Connected to {self.uri}")
            return True
        except ConnectionRefusedError:
            log_error(f"Failed to connect to {self.uri}")
            return False

    async def close(self):
        if self.open:
            await self.websocket.close()

        await super().close()

    async def send_data(self, data: str):
        if await self.ensure_connection():
            await self.websocket.send(data)

    async def ensure_connection(self) -> bool:
        return self.open or await self.connect()
