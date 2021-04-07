from typing import TYPE_CHECKING, Type, Dict, Tuple


if TYPE_CHECKING:
    from .command_class import CommandClass


class CommandClassFactory:
    def __init__(self):
        self.command_classes: Dict[Tuple[int, int], Type['CommandClass']] = {}

    def register(self, cls: Type['CommandClass']):
        self.command_classes[(cls.class_id, cls.class_version)] = cls

    def find_command_class(self, class_id: int, version: int) -> Type['CommandClass']:
        return self.command_classes[(class_id, version)]


command_class_factory = CommandClassFactory()
