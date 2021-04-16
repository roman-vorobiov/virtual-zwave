from dataclasses import dataclass, replace
from typing import List, Optional


@dataclass
class Context:
    node_id: int = 0
    endpoint: int = 0
    multi_cmd_response_queue: Optional[List[List[int]]] = None
    secure: bool = False

    def copy(self, **kwargs):
        return replace(self, **kwargs)
