from abc import ABC, abstractmethod


class RemoteInterface(ABC):
    @abstractmethod
    def send_message(self, message: dict):
        pass
