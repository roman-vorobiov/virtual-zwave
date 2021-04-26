from ..node_repository import NodeRepository

from network.application import Node, NodeFactory, NodeBuilder

import uuid
from tinydb import TinyDB, Query
from typing import Optional, List


def where(**kwargs) -> Query:
    return Query().fragment(kwargs)


class NodeDatabase(NodeRepository):
    def __init__(self, db: TinyDB, node_factory: NodeFactory):
        self.table = db.table('nodes')
        self.node_builder = NodeBuilder(node_factory)
        self.cache = {node_info['id']: self.from_record(node_info) for node_info in self.load()}

    def add(self, node: Node):
        node.id = self.generate_id()
        node.repository = self
        self.table.insert(node.to_dict())
        self.cache[node.id] = node

    def remove(self, id: str):
        self.table.remove(where(id=id))
        del self.cache[id]

    def update(self, node: Node):
        self.table.update(node.to_dict(), where(id=node.id))

    def get(self, id: str) -> Optional[Node]:
        return self.cache.get(id)

    def find(self, home_id: int, node_id: int) -> Optional[Node]:
        for node in self.cache.values():
            if node.home_id == home_id and node.node_id == node_id:
                return node

    def all(self) -> List[Node]:
        return list(self.cache.values())

    def get_nodes_in_home(self, home_id: int) -> List[Node]:
        return list(filter(lambda node: node.home_id == home_id, self.cache.values()))

    def clear(self):
        self.table.truncate()
        self.cache.clear()

    def from_record(self, record: dict) -> Node:
        node = self.node_builder.from_dict(record)
        node.id = record['id']
        node.repository = self

        return node

    def load(self) -> List[dict]:
        return self.table.all()

    @classmethod
    def generate_id(cls) -> str:
        return str(uuid.uuid4())
