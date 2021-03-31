from abc import ABC, abstractmethod
from typing import Optional, Any


class State(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any):
        pass

    @abstractmethod
    def empty(self) -> bool:
        pass

    @abstractmethod
    def clear(self):
        pass
