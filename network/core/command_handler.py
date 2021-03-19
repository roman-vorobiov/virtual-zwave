from common import Network

from tools import log_error


class CommandHandler:
    def __init__(self, network: Network):
        self.network = network

    def handle_command(self, command: str):
        handlers = {
            'nif': self.send_nif
        }

        handlers.get(command, self.handle_unknown_command)()

    def send_nif(self):
        self.network.send_message({'args': "hello"})

    def handle_unknown_command(self):
        log_error("Unknown command")
