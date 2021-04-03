from typing import TYPE_CHECKING, Type, Dict, Tuple


if TYPE_CHECKING:
    from .command_class import CommandClass
    from ..node import Channel


class CommandClassFactory:
    def __init__(self):
        self.command_classes: Dict[Tuple[int, int], type] = {}

    def register(self, cls: Type['CommandClass']):
        self.command_classes[(cls.class_id, cls.class_version)] = cls

    def create_command_class(self, class_id: int, version: int, channel: 'Channel', **kwargs) -> 'CommandClass':
        cls = self.command_classes[(class_id, version)]
        cc = cls(channel, **kwargs)
        channel.add_command_class(cc)
        return cc


command_class_factory = CommandClassFactory()
