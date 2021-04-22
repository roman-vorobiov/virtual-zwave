from ..fixtures import *

from network.application import Channel
from network.application.utils import AgiProfile, AssociationGroup

from network.application.command_classes.application.binary_switch import BinarySwitch1
from network.application.command_classes.management.association import Association1, Association2


def add_association_group(channel: Channel, /, **kwargs):
    group = AssociationGroup(**kwargs)
    channel.associations.groups.append(group)
    return group


@pytest.fixture(scope='class', autouse=True)
def lifeline(channel):
    yield add_association_group(channel, name="Lifeline", profile=(AgiProfile.General, 0x01), commands=[])


@pytest.fixture(scope='class', autouse=True)
def association_group_2(channel, lifeline):
    yield add_association_group(channel, name="Group 2", profile=(AgiProfile.General, 0x00), commands=[])


@pytest.fixture
def clear_associations(channel):
    yield
    channel.associations.clear_all()


@pytest.fixture(scope='class')
def binary_switch(channel):
    yield channel.add_command_class(BinarySwitch1)


class TestAssociation1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel, binary_switch):
        yield channel.add_command_class(Association1)

    def test_set(self, rx, tx, lifeline, association_group_2):
        rx('ASSOCIATION_SET', group_id=1, node_ids=[1, 3])
        assert lifeline.targets == [(1, 0), (3, 0)]
        assert association_group_2.targets == []

        rx('ASSOCIATION_SET', group_id=1, node_ids=[3, 4])
        assert lifeline.targets == [(1, 0), (3, 0), (4, 0)]
        assert association_group_2.targets == []

    def test_get(self, rx, tx, lifeline):
        lifeline.targets = [(1, 0), (3, 0)]

        rx('ASSOCIATION_GET', group_id=1)
        tx('ASSOCIATION_REPORT', group_id=1, max_nodes_supported=255, reports_to_follow=0, node_ids=[1, 3])

    def test_remove_from_all_groups(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        # Unsupported
        rx('ASSOCIATION_REMOVE', group_id=0, node_ids=[1, 3])
        assert lifeline.targets == [(1, 0), (3, 0), (4, 0)]
        assert association_group_2.targets == [(3, 0), (4, 0), (5, 0)]

    def test_remove_from_group(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        rx('ASSOCIATION_REMOVE', group_id=1, node_ids=[1, 3])
        assert lifeline.targets == [(4, 0)]
        assert association_group_2.targets == [(3, 0), (4, 0), (5, 0)]

    def test_remove_all_nodes_from_all_groups(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        # Unsupported
        rx('ASSOCIATION_REMOVE', group_id=0, node_ids=[])
        assert lifeline.targets == [(1, 0), (3, 0), (4, 0)]
        assert association_group_2.targets == [(3, 0), (4, 0), (5, 0)]

    def test_remove_all_nodes_from_group(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        rx('ASSOCIATION_REMOVE', group_id=1, node_ids=[])
        assert lifeline.targets == []
        assert association_group_2.targets == [(3, 0), (4, 0), (5, 0)]

    def test_groupings_get(self, rx, tx):
        rx('ASSOCIATION_GROUPINGS_GET')
        tx('ASSOCIATION_GROUPINGS_REPORT', supported_groups=2)

    def test_unsolicited_report(self, tx, tx_client, node, lifeline, binary_switch):
        lifeline.targets = [(1, 0)]
        lifeline.commands = [(0x25, 0x03)]

        binary_switch.update_state(value=0x00)
        tx('SWITCH_BINARY_REPORT', BinarySwitch1.class_id, value=0x00)
        tx_client('NODE_UPDATED', {'node': node.to_json()})


class TestAssociation2:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel, binary_switch):
        yield channel.add_command_class(Association2)

    def test_remove_from_all_groups(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        rx('ASSOCIATION_REMOVE', group_id=0, node_ids=[1, 3])
        assert lifeline.targets == [(4, 0)]
        assert association_group_2.targets == [(4, 0), (5, 0)]

    def test_remove_from_group(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        rx('ASSOCIATION_REMOVE', group_id=1, node_ids=[1, 3])
        assert lifeline.targets == [(4, 0)]
        assert association_group_2.targets == [(3, 0), (4, 0), (5, 0)]

    def test_remove_all_nodes_from_all_groups(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        rx('ASSOCIATION_REMOVE', group_id=0, node_ids=[])
        assert lifeline.targets == []
        assert association_group_2.targets == []

    def test_remove_all_nodes_from_group(self, rx, tx, lifeline, association_group_2):
        lifeline.targets = [(1, 0), (3, 0), (4, 0)]
        association_group_2.targets = [(3, 0), (4, 0), (5, 0)]

        rx('ASSOCIATION_REMOVE', group_id=1, node_ids=[])
        assert lifeline.targets == []
        assert association_group_2.targets == [(3, 0), (4, 0), (5, 0)]

    def test_specific_group_get(self, rx, tx):
        rx('ASSOCIATION_SPECIFIC_GROUP_GET')
        tx('ASSOCIATION_SPECIFIC_GROUP_REPORT', group_id=0)
