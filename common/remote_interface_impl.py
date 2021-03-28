from .remote_interface import RemoteInterface

from tools.websockets import RemoteConnection

import json
import asyncio


class RemoteInterfaceImpl(RemoteInterface):
    def __init__(self, connection: RemoteConnection):
        self.connection = connection

    def send_message(self, message: dict):
        data = json.dumps(message)
        asyncio.create_task(self.connection.send_data(data))
