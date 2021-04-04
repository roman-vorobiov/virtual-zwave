from ..node_repository import NodeRepository

from network.application import Node, NodeFactory, ChannelFactory, make_command_class

import uuid
from tinydb import TinyDB, Query
from typing import Optional, List


def where(**kwargs) -> Query:
    return Query().fragment(kwargs)


class NodeDatabase(NodeRepository):
    def __init__(self, db: TinyDB, node_factory: NodeFactory, channel_factory: ChannelFactory):
        self.table = db.table('nodes')
        self.node_factory = node_factory
        self.channel_factory = channel_factory

    def add(self, node: Node):
        node.id = self.generate_id()
        node.repository = self
        self.table.insert(node.to_dict())

    def remove(self, home_id: int, node_id: int) -> Optional[Node]:
        node = self.find(home_id, node_id)

        if node is not None:
            self.table.remove(where(id=node.id))

        return node

    def update(self, node: Node):
        self.table.update(node.to_dict(), where(id=node.id))

    def get(self, id: int) -> Optional[Node]:
        if (record := self.table.get(where(id=id))) is not None:
            return self.from_record(record)

    def find(self, home_id: int, node_id: int) -> Optional[Node]:
        if (record := self.table.get(where(home_id=home_id, node_id=node_id))) is not None:
            return self.from_record(record)

    def all(self) -> List[dict]:
        return self.table.all()

    def get_node_ids(self, home_id: int) -> List[int]:
        query = Query()
        return [record['node_id'] for record in self.table.search(query.home_id == home_id)]

    def clear(self):
        self.table.truncate()

    def from_record(self, record: dict) -> Node:
        node = self.node_factory.create_node(record['basic'])
        node.id = record['id']
        node.repository = self

        node.add_to_network(record['home_id'], record['node_id'])
        node.set_suc_node_id(record['suc_node_id'])

        for channel_record in record['channels']:
            channel = self.channel_factory.create_channel(node, channel_record['generic'], channel_record['specific'])

            for class_id, args in channel_record['command_classes'].items():
                version = args.pop('class_version')
                make_command_class(int(class_id), version, channel, **args)
                args['class_version'] = version

        return node

    @classmethod
    def generate_id(cls) -> str:
        return str(uuid.uuid4())
