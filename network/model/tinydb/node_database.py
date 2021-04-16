from ..node_repository import NodeRepository

from network.application import Node, NodeFactory, command_class_factory

import uuid
from tinydb import TinyDB, Query
from typing import Optional, List


def where(**kwargs) -> Query:
    return Query().fragment(kwargs)


class NodeDatabase(NodeRepository):
    def __init__(self, db: TinyDB, node_factory: NodeFactory):
        self.table = db.table('nodes')
        self.node_factory = node_factory
        self.cache = {node_info['id']: self.from_record(node_info) for node_info in self.all()}

    def add(self, node: Node):
        node.id = self.generate_id()
        node.repository = self
        self.table.insert(node.to_dict())
        self.cache[node.id] = node

    def remove(self, home_id: int, node_id: int) -> Optional[Node]:
        node = self.find(home_id, node_id)

        if node is not None:
            self.table.remove(where(id=node.id))
            return self.cache.pop(node.id)

    def update(self, node: Node):
        self.table.update(node.to_dict(), where(id=node.id))

    def get(self, id: str) -> Optional[Node]:
        return self.cache.get(id)

    def find(self, home_id: int, node_id: int) -> Optional[Node]:
        for node in self.cache.values():
            if node.home_id == home_id and node.node_id == node_id:
                return node

    def all(self) -> List[dict]:
        return self.table.all()

    def get_node_ids(self, home_id: int) -> List[int]:
        return [node.node_id for node in self.cache.values() if node.home_id == home_id]

    def clear(self):
        self.table.truncate()
        self.cache.clear()

    def from_record(self, record: dict) -> Node:
        node = self.node_factory.create_node()
        node.id = record['id']
        node.repository = self

        node.__setstate__(record)

        for channel_record in record['channels']:
            channel = node.add_channel(channel_record['generic'], channel_record['specific'])

            for class_id, args in channel_record['command_classes'].items():
                version = args.pop('class_version')
                cls = command_class_factory.find_command_class(int(class_id), version)
                channel.add_command_class(cls, **args)
                args['class_version'] = version

        return node

    @classmethod
    def generate_id(cls) -> str:
        return str(uuid.uuid4())
