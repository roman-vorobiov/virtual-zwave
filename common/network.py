from tools.websockets import NetworkConnection

import json


class Network:
    def __init__(self, connection: NetworkConnection):
        self.connection = connection

    async def send_message(self, message: dict):
        data = json.dumps(message)
        await self.connection.send_data(data)
