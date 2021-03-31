from ..repository_provider import RepositoryProvider
from .node_info_database import NodeInfoDatabase
from .persistent_state import PersistentState

from common.tinydb import BaseDatabaseProvider


class DatabaseProvider(RepositoryProvider, BaseDatabaseProvider):
    def __init__(self):
        BaseDatabaseProvider.__init__(self, ".storage/controller.json")

    def get_state(self) -> PersistentState:
        return PersistentState(self.db)

    def get_node_infos(self) -> NodeInfoDatabase:
        return NodeInfoDatabase(self.db)
