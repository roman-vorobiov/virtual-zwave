from tools.websockets import NetworkServerConnection

import asyncio
import json
from threading import Thread
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="network/client/src", **kwargs)

    def log_message(self, fmt: str, *args):
        pass


class Client:
    def __init__(self):
        self.httpd = ThreadingHTTPServer(('localhost', 3000), Handler)
        self.connection = NetworkServerConnection(7654)

    async def initialize(self):
        await self.connection.initialize()

        job = Thread(target=self.httpd.serve_forever)
        job.start()

    async def stop(self):
        self.httpd.shutdown()
        await self.connection.close()

    def send_message(self, message_type: str, details: dict):
        data = {
            'messageType': message_type,
            'message': details
        }

        asyncio.create_task(self.connection.send_data(json.dumps(data)))

    def poll(self):
        return self.connection.poll()
