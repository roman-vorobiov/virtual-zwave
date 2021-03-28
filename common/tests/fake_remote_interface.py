from common import RemoteInterface

from typing import List


class FakeRemoteInterface(RemoteInterface):
    def __init__(self):
        self.tx_buffer = []

    def send_message(self, message: dict):
        self.tx_buffer.append(message)

    def free_buffer(self) -> List[dict]:
        self.tx_buffer, old_buffer = [], self.tx_buffer
        return old_buffer
