from ..node_info_repository import NodeInfoRepository

from tools import Object

from tinydb import TinyDB, Query
from typing import Optional, List


def where(**kwargs) -> Query:
    return Query().fragment(kwargs)


class NodeInfoDatabase(NodeInfoRepository):
    def __init__(self, db: TinyDB):
        self.table = db.table('node_infos')

    def add(self, node_id: int, node_info: Object):
        self.table.insert({'node_id': node_id, 'node_info': node_info.get_data()})

    def remove(self, node_id: int) -> Optional[Object]:
        node_info = self.find(node_id)

        if node_info is not None:
            self.table.remove(where(node_id=node_id))

        return node_info

    def find(self, node_id: int) -> Optional[Object]:
        if (record := self.table.get(where(node_id=node_id))) is not None:
            return self.from_record(record)

    def get_node_ids(self) -> List[int]:
        return [record['node_id'] for record in self.table.all()]

    def clear(self):
        self.table.truncate()

    @classmethod
    def from_record(cls, record: dict) -> Object:
        return Object(data=record['node_info'], meta={'node_id': record['node_id']})
