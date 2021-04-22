from tools import Serializable

from enum import IntEnum
from dataclasses import dataclass, field
from typing import List, Tuple, Iterator


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

    @property
    def group_ids(self) -> Iterator[int]:
        return range(1, len(self.groups) + 1)

    def get_destinations(self, group_id: int) -> List[int]:
        group = self.get_group(group_id)
        return [node_id for node_id, _ in group.targets]

    def get_group(self, group_id: int) -> AssociationGroup:
        return self.groups[group_id - 1]

    def subscribe(self, group_id: int, node_id: int, endpoint=0):
        key = (node_id, endpoint)
        group = self.get_group(group_id)

        if key not in group.targets:
            group.targets.append(key)

    def unsubscribe(self, group_id: int, node_id: int, endpoint=0):
        key = (node_id, endpoint)
        group = self.get_group(group_id)

        try:
            group.targets.remove(key)
        except ValueError:
            pass

    def unsubscribe_from_all(self, node_id: int):
        for group_id in self.group_ids:
            self.unsubscribe(group_id, node_id)

    def clear_association_in_group(self, group_id: int):
        self.get_group(group_id).targets.clear()

    def clear_all(self):
        for group in self.groups:
            group.targets.clear()

    def find_targets(self, class_id: int, command_id: int):
        for group in self.groups:
            if (class_id, command_id) in group.commands:
                yield from group.targets
