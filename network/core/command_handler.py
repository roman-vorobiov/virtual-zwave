from common.network import Network

import json


class CommandHandler:
    def __init__(self, network: Network):
        self.network = network

    def handle_message(self, data: str):
        message = json.loads(data)
        print(f"RX: {message}")
