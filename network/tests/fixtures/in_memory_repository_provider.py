from network.model import RepositoryProvider
from network.model.tinydb import NodeDatabase

from network.application import NodeFactory

from tinydb import TinyDB
from tinydb.storages import MemoryStorage


class InMemoryRepositoryProvider(RepositoryProvider):
    def __init__(self, node_factory: NodeFactory):
        self.db = TinyDB(storage=MemoryStorage)
        self.node_factory = node_factory

    def get_nodes(self) -> NodeDatabase:
        return NodeDatabase(self.db, self.node_factory)
