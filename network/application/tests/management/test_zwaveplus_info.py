from ..fixtures import *

from network.application.command_classes.management import ZWavePlusInfo2


class TestZWavePlusInfo2:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(ZWavePlusInfo2,
                                        zwave_plus_version=1,
                                        role_type=2,
                                        node_type=3,
                                        installer_icon_type=4,
                                        user_icon_type=5)

    def test_zwaveplus_info_get(self, rx, tx):
        rx('ZWAVEPLUS_INFO_GET')
        tx('ZWAVEPLUS_INFO_REPORT',
           zwave_plus_version=1, role_type=2, node_type=3, installer_icon_type=4, user_icon_type=5)
