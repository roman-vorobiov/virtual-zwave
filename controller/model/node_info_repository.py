from tools import Object

from abc import ABC, abstractmethod
from typing import Optional, List


class NodeInfoRepository(ABC):
    @abstractmethod
    def add(self, node_id: int, node_info: Object):
        pass

    @abstractmethod
    def remove(self, node_id: int) -> Optional[Object]:
        pass

    @abstractmethod
    def find(self, node_id: int) -> Optional[Object]:
        pass

    @abstractmethod
    def get_node_ids(self) -> List[int]:
        pass

    @abstractmethod
    def clear(self):
        pass
