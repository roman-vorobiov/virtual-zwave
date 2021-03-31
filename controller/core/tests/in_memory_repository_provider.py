from controller.model.repository_provider import RepositoryProvider

from controller.model.tinydb import NodeInfoDatabase, PersistentState

from tinydb import TinyDB
from tinydb.storages import MemoryStorage


class InMemoryRepositoryProvider(RepositoryProvider):
    def __init__(self):
        self.db = TinyDB(storage=MemoryStorage)

    def get_state(self) -> PersistentState:
        return PersistentState(self.db)

    def get_node_infos(self) -> NodeInfoDatabase:
        return NodeInfoDatabase(self.db)
