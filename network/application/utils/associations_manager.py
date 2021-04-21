from tools import Serializable

from enum import IntEnum
from dataclasses import dataclass, field
from typing import List, Tuple


class AgiProfile(IntEnum):
    General = 0x00
    Control = 0x20
    Sensor = 0x31
    Notification = 0x71
    Meter = 0x32
    Irrigation = 0x68


@dataclass
class AssociationGroup(Serializable):
    name: str
    profile: Tuple[AgiProfile, int]
    commands: List[Tuple[int, int]]
    targets: List[Tuple[int, int]] = field(default_factory=list)

    def __getstate__(self):
        return {
            'name': self.name,
            'profile': self.profile,
            'commands': self.commands,
            'targets': self.targets
        }


class AssociationsManager:
    def __init__(self, groups: List[AssociationGroup]):
        self.groups = groups

    def subscribe(self, group_id: int, node_id: int, endpoint=0):
        key = (node_id, endpoint)
        group = self.groups[group_id]

        if key not in group.targets:
            group.targets.append(key)

    def unsubscribe(self, group_id: int, node_id: int, endpoint=0):
        key = (node_id, endpoint)
        group = self.groups[group_id]

        try:
            group.targets.remove(key)
        except ValueError:
            pass

    def get_targets(self, class_id: int, command_id: int):
        for group in self.groups:
            if (class_id, command_id) in group.commands:
                yield from group.targets
