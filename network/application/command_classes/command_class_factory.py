from typing import TYPE_CHECKING, Type, Dict


if TYPE_CHECKING:
    from .command_class import CommandClass
    from ..node import Node


class CommandClassFactory:
    def __init__(self):
        self.command_classes: Dict[str, type] = {}

    def register(self, name: str, cls: Type['CommandClass']):
        self.command_classes[name] = cls

    def create_command_class(self, name: str, node: 'Node', **kwargs) -> 'CommandClass':
        cls = self.command_classes[name]
        cc = cls(node, **kwargs)
        node.add_command_class(cc)
        return cc


command_class_factory = CommandClassFactory()
