from .remote_connection import RemoteConnection

from tools import log_info

import websockets
from websockets import WebSocketServer, WebSocketServerProtocol
from typing import Optional


class RemoteServer(RemoteConnection):
    def __init__(self, port: int):
        super().__init__()
        self.port = port
        self.server: Optional[WebSocketServer] = None

    async def initialize(self):
        super().initialize()
        await self.serve()

    async def close(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            log_info("Websocket closed")

        await super().close()

    async def send_data(self, data: str):
        if self.open:
            await self.websocket.send(data)

    async def serve(self):
        if self.server is None:
            self.server = await websockets.serve(self.on_new_connection, "localhost", self.port)
            log_info(f"Websocket opened at ws://localhost:{self.port}")

    async def on_new_connection(self, websocket: WebSocketServerProtocol, path: str):
        log_info("Client connected")

        self.websocket = websocket
        await self.start_polling()

        log_info("Connection closed")
