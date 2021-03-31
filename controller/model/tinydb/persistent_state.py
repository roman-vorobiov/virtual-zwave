from ..state import State

from tinydb import TinyDB, Query
from typing import Optional, Any


def where(**kwargs) -> Query:
    return Query().fragment(kwargs)


class PersistentState(State):
    def __init__(self, db: TinyDB):
        self.table = db.table('state')

    def get(self, key: str) -> Optional[Any]:
        if (record := self.table.get(where(key=key))) is not None:
            return record['value']

    def set(self, key: str, value: Any):
        self.table.upsert({'key': key, 'value': value}, where(key=key))

    def empty(self) -> bool:
        return len(self.table) == 0

    def clear(self):
        self.table.truncate()
