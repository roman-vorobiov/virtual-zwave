from ..fixtures import *

from network.application import Channel
from network.application.utils import AgiProfile, AssociationGroup

from network.application.command_classes.management.association_group_info import AssociationGroupInfo1


def add_association_group(channel: Channel, /, **kwargs):
    group = AssociationGroup(**kwargs)
    channel.associations.groups.append(group)
    return group


@pytest.fixture(scope='class', autouse=True)
def lifeline(channel):
    yield add_association_group(channel, name="Lifeline", profile=(AgiProfile.General, 0x01), commands=[(0x25, 0x03)])


@pytest.fixture(scope='class', autouse=True)
def association_group_2(channel, lifeline):
    yield add_association_group(channel, name="Group 2", profile=(AgiProfile.General, 0x00), commands=[])


@pytest.fixture
def clear_associations(channel):
    yield
    channel.associations.clear_all()


class TestAssociationGroupInfo1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(AssociationGroupInfo1)

    def test_name_get(self, rx, tx):
        rx('ASSOCIATION_GROUP_NAME_GET', group_id=1)
        tx('ASSOCIATION_GROUP_NAME_REPORT', group_id=1, name="Lifeline")

    def test_info_get_single(self, rx, tx):
        rx('ASSOCIATION_GROUP_INFO_GET', group_id=1, list_mode=False, refresh_cache=False)
        tx('ASSOCIATION_GROUP_INFO_REPORT', list_mode=False, dynamic_info=False, groups=[
            make_object(group_id=1, profile=make_object(generic=0x00, specific=0x01))
        ])

    def test_info_get_all(self, rx, tx):
        rx('ASSOCIATION_GROUP_INFO_GET', group_id=1, list_mode=True, refresh_cache=False)
        tx('ASSOCIATION_GROUP_INFO_REPORT', list_mode=True, dynamic_info=False, groups=[
            make_object(group_id=1, profile=make_object(generic=0x00, specific=0x01)),
            make_object(group_id=2, profile=make_object(generic=0x00, specific=0x00))
        ])

    def test_command_list_get(self, rx, tx):
        rx('ASSOCIATION_GROUP_COMMAND_LIST_GET', group_id=1, allow_cache=False)
        tx('ASSOCIATION_GROUP_COMMAND_LIST_REPORT', group_id=1, commands=[
            make_object(class_id=0x25, command_id=0x03)
        ])
