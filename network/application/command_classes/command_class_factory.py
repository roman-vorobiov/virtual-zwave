from typing import TYPE_CHECKING, Type, Dict, Tuple


if TYPE_CHECKING:
    from .command_class import CommandClass
    from ..node import Node


class CommandClassFactory:
    def __init__(self):
        self.command_classes: Dict[Tuple[int, int], type] = {}

    def register(self, cls: Type['CommandClass']):
        self.command_classes[(cls.class_id, cls.class_version)] = cls

    def create_command_class(self, class_id: int, version: int, node: 'Node', **kwargs) -> 'CommandClass':
        cls = self.command_classes[(class_id, version)]
        cc = cls(node, **kwargs)
        node.add_command_class(cc)
        return cc


command_class_factory = CommandClassFactory()
