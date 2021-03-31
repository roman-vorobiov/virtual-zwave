from .node_info_repository import NodeInfoRepository
from .state import State

from abc import ABC, abstractmethod


class RepositoryProvider(ABC):
    @abstractmethod
    def get_state(self) -> State:
        pass

    @abstractmethod
    def get_node_infos(self) -> NodeInfoRepository:
        pass
