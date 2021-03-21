from abc import ABC, abstractmethod


class Network(ABC):
    @abstractmethod
    def send_message(self, message: dict):
        pass
