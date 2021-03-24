from ..fixture import *

from network.application.command_classes.command_class_factory import command_class_factory


@pytest.fixture(autouse=True)
def command_class(node):
    yield command_class_factory.create_command_class('COMMAND_CLASS_ZWAVEPLUS_INFO',
                                                     node,
                                                     zwave_plus_version=1,
                                                     role_type=2,
                                                     node_type=3,
                                                     installer_icon_type=4,
                                                     user_icon_type=5)


def test_zwaveplus_info_get(rx, tx):
    rx('ZWAVEPLUS_INFO_GET')
    tx('ZWAVEPLUS_INFO_REPORT', zwave_plus_version=1, role_type=2, node_type=3, installer_icon_type=4, user_icon_type=5)
