from tools import Serializable

from collections import defaultdict
from enum import IntEnum
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Iterator


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
    targets: defaultdict[int, Set[int]] = field(default_factory=lambda: defaultdict(set))

    def __getstate__(self):
        return {
            'name': self.name,
            'profile': self.profile,
            'commands': self.commands,
            'targets': dict(self.sorted_targets)
        }

    @property
    def sorted_targets(self) -> Iterator[Tuple[int, List[int]]]:
        for node_id, endpoints in self.targets.items():
            yield node_id, sorted(endpoints)


class AssociationsManager:
    def __init__(self, groups: List[AssociationGroup]):
        self.groups = groups

    @property
    def group_ids(self) -> Iterator[int]:
        return range(1, len(self.groups) + 1)

    def get_destinations(self, group_id: int) -> Iterator[Tuple[int, List[int]]]:
        yield from self.get_group(group_id).sorted_targets

    def get_group(self, group_id: int) -> AssociationGroup:
        return self.groups[group_id - 1]

    def subscribe(self, group_id: int, node_id: int, endpoints=None):
        group = self.get_group(group_id)

        group.targets[node_id].update(endpoints or [0])

    def unsubscribe(self, group_id: int, node_id: int, endpoints=None):
        group = self.get_group(group_id)

        group.targets[node_id].difference_update(endpoints or [0])

        if len(group.targets[node_id]) == 0:
            del group.targets[node_id]

    def unsubscribe_from_all(self, node_id: int, endpoints=None):
        for group_id in self.group_ids:
            self.unsubscribe(group_id, node_id, endpoints)

    def clear_association_in_group(self, group_id: int):
        self.get_group(group_id).targets.clear()

    def clear_all(self):
        for group in self.groups:
            group.targets.clear()

    def find_targets(self, class_id: int, command_id: int) -> Iterator[Tuple[int, List[int]]]:
        for group in self.groups:
            if (class_id, command_id) in group.commands:
                yield from group.sorted_targets
