from network.application import Node

from abc import ABC, abstractmethod
from typing import Optional, List


class NodeRepository(ABC):
    @abstractmethod
    def add(self, node: Node):
        pass

    @abstractmethod
    def remove(self, id: str):
        pass

    @abstractmethod
    def update(self, node: Node):
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[Node]:
        pass

    @abstractmethod
    def find(self, home_id: int, node_id: int) -> Optional[Node]:
        pass

    @abstractmethod
    def all(self) -> List[Node]:
        pass

    @abstractmethod
    def get_nodes_in_home(self, home_id: int) -> List[Node]:
        pass

    @abstractmethod
    def clear(self):
        pass
