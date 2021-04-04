from ..repository_provider import RepositoryProvider
from .node_database import NodeDatabase

from network.application import NodeFactory, ChannelFactory

from common.tinydb import BaseDatabaseProvider


class DatabaseProvider(RepositoryProvider, BaseDatabaseProvider):
    def __init__(self, node_factory: NodeFactory, channel_factory: ChannelFactory):
        BaseDatabaseProvider.__init__(self, ".storage/network.json")
        self.node_factory = node_factory
        self.channel_factory = channel_factory

    def get_nodes(self) -> NodeDatabase:
        return NodeDatabase(self.db, self.node_factory, self.channel_factory)
