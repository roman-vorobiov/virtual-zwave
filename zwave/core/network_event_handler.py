from common import Network

from tools import log_warning

import json


class NetworkEventHandler:
    def __init__(self, network: Network):
        self.network = network

    def process_message(self, message: str):
        command = json.loads(message)
        log_warning(f"{command}")
