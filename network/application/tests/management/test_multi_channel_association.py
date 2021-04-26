from ..fixtures import *

from network.application import Channel
from network.application.utils import AgiProfile, AssociationGroup

from network.application.command_classes.application.binary_switch import BinarySwitch1
from network.application.command_classes.management.multi_channel_association import MultiChannelAssociation2

from tools import make_object


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


@pytest.fixture(autouse=True)
def seed_associations(lifeline, association_group_2):
    lifeline.targets.update({1: {0, 1}, 3: {1, 2}, 4: {3}})
    association_group_2.targets.update({3: {0, 1}, 4: {1, 2}, 5: {8}})

    yield

    lifeline.targets.clear()
    association_group_2.targets.clear()


@pytest.fixture(scope='class')
def binary_switch(channel):
    yield channel.add_command_class(BinarySwitch1)


class TestAssociation1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel, binary_switch):
        yield channel.add_command_class(MultiChannelAssociation2)

    def test_set(self, rx, tx, tx_client, node, lifeline, association_group_2):
        rx('MULTI_CHANNEL_ASSOCIATION_SET',
           group_id=1,
           node_ids=[4, 5],
           multi_channel_destinations=[
               make_object(node_id=3, bit_address=False, endpoint=4),
               make_object(node_id=5, bit_address=True, endpoint=0b00000101)
           ])
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })

        assert lifeline.targets == {1: {0, 1}, 3: {1, 2, 4}, 4: {0, 3}, 5: {0, 1, 3}}
        assert association_group_2.targets == {3: {0, 1}, 4: {1, 2}, 5: {8}}

    def test_get(self, rx, tx, lifeline, association_group_2):
        rx('MULTI_CHANNEL_ASSOCIATION_GET', group_id=2)
        tx('MULTI_CHANNEL_ASSOCIATION_REPORT',
           group_id=2,
           max_nodes_supported=255,
           reports_to_follow=0,
           node_ids=[3],
           multi_channel_destinations=[
               make_object(node_id=3, endpoint=0b00000001, bit_address=True),
               make_object(node_id=4, endpoint=0b00000011, bit_address=True),
               make_object(node_id=5, endpoint=8, bit_address=False)
           ])

    def test_remove_from_all_groups(self, rx, tx, tx_client, node, lifeline, association_group_2):
        rx('MULTI_CHANNEL_ASSOCIATION_REMOVE',
           group_id=0,
           node_ids=[3],
           multi_channel_destinations=[
               make_object(node_id=4, endpoint=0b00000011, bit_address=True)
           ])
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })

        assert lifeline.targets == {1: {0, 1}, 3: {1, 2}, 4: {3}}
        assert association_group_2.targets == {3: {1}, 5: {8}}

    def test_remove_from_group(self, rx, tx, tx_client, node, lifeline, association_group_2):
        rx('MULTI_CHANNEL_ASSOCIATION_REMOVE',
           group_id=1,
           node_ids=[1],
           multi_channel_destinations=[
               make_object(node_id=4, endpoint=3, bit_address=False)
           ])
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })

        assert lifeline.targets == {1: {1}, 3: {1, 2}}
        assert association_group_2.targets == {3: {0, 1}, 4: {1, 2}, 5: {8}}

    def test_remove_all_nodes_from_all_groups(self, rx, tx, tx_client, node, lifeline, association_group_2):
        rx('MULTI_CHANNEL_ASSOCIATION_REMOVE',
           group_id=0,
           node_ids=[],
           multi_channel_destinations=[])
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })

        assert lifeline.targets == {}
        assert association_group_2.targets == {}

    def test_remove_all_nodes_from_group(self, rx, tx, tx_client, node, lifeline, association_group_2):
        rx('MULTI_CHANNEL_ASSOCIATION_REMOVE',
           group_id=1,
           node_ids=[],
           multi_channel_destinations=[])
        tx_client('NODE_UPDATED', {
            'node': node.to_json()
        })

        assert lifeline.targets == {}
        assert association_group_2.targets == {3: {0, 1}, 4: {1, 2}, 5: {8}}

    def test_groupings_get(self, rx, tx):
        rx('MULTI_CHANNEL_ASSOCIATION_GROUPINGS_GET')
        tx('MULTI_CHANNEL_ASSOCIATION_GROUPINGS_REPORT', supported_groups=2)

