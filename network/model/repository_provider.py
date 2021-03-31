from .node_repository import NodeRepository

from abc import ABC, abstractmethod


class RepositoryProvider(ABC):
    @abstractmethod
    def get_nodes(self) -> NodeRepository:
        pass
