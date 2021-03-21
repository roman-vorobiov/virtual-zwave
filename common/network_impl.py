from .network import Network

from tools.websockets import NetworkConnection

import json
import asyncio


class NetworkImpl(Network):
    def __init__(self, connection: NetworkConnection):
        self.connection = connection

    def send_message(self, message: dict):
        data = json.dumps(message)
        asyncio.create_task(self.connection.send_data(data))
