from ..fixtures import *

from network.application import make_command_class

from network.application.command_classes.management import Version1, Version2, Version3

from tools import make_object


class TestVersion1:
    @pytest.fixture(autouse=True)
    def command_class(self, channel):
        yield Version1(channel,
                       protocol_library_type=0x06,
                       protocol_version=(1, 2),
                       application_version=(3, 4))

    def test_version_get(self, rx, tx):
        rx('VERSION_GET')
        tx('VERSION_REPORT',
           protocol_library_type=0x06,
           protocol_version=make_object(major=1, minor=2),
           application_version=make_object(major=3, minor=4))

    def test_version_command_class_get_supported(self, rx, tx):
        rx('VERSION_COMMAND_CLASS_GET', class_id=0x86)
        tx('VERSION_COMMAND_CLASS_REPORT', class_id=0x86, version=1)

    def test_version_command_class_get_unsupported(self, rx, tx):
        rx('VERSION_COMMAND_CLASS_GET', class_id=0x84)
        tx('VERSION_COMMAND_CLASS_REPORT', class_id=0x84, version=0)

    def test_version_command_class_get_other_channel(self, rx, tx, make_channel):
        channel2 = make_channel()
        make_command_class(0x20, 1, channel2)

        rx('VERSION_COMMAND_CLASS_GET', class_id=0x20)
        tx('VERSION_COMMAND_CLASS_REPORT', class_id=0x20, version=1)


class TestVersion2:
    @pytest.fixture(autouse=True)
    def command_class(self, channel):
        yield Version2(channel,
                       protocol_library_type=0x06,
                       protocol_version=(1, 2),
                       application_version=(3, 4),
                       hardware_version=5,
                       firmware_versions=[(6, 7), (8, 9)])

    def test_version_get(self, rx, tx):
        rx('VERSION_GET')
        tx('VERSION_REPORT',
           protocol_library_type=0x06,
           protocol_version=make_object(major=1, minor=2),
           application_version=make_object(major=3, minor=4),
           hardware_version=5,
           firmware_versions=[
               make_object(major=6, minor=7),
               make_object(major=8, minor=9)
           ])


class TestVersion3NoSoftware:
    @pytest.fixture(autouse=True)
    def command_class(self, channel):
        yield Version3(channel,
                       protocol_library_type=0x06,
                       protocol_version=(1, 2),
                       application_version=(3, 4),
                       hardware_version=5,
                       firmware_versions=[
                           (6, 7),
                           (8, 9)
                       ])

    def test_capabilities_get(self, rx, tx):
        rx('VERSION_CAPABILITIES_GET')
        tx('VERSION_CAPABILITIES_REPORT', zwave_software=False, command_class=True, version=True)

    def test_software_get(self, rx, tx):
        rx('VERSION_ZWAVE_SOFTWARE_GET')


class TestVersion3WithSoftware:
    @pytest.fixture(autouse=True)
    def command_class(self, channel):
        yield Version3(channel,
                       protocol_library_type=0x06,
                       protocol_version=(1, 2),
                       application_version=(3, 4),
                       hardware_version=5,
                       firmware_versions=[
                           (6, 7),
                           (8, 9)
                       ],
                       sdk_version=(1, 2, 3),
                       zwave_application_framework_api_version=(2, 3, 4),
                       zwave_application_framework_build_number=1,
                       host_interface_api_version=(3, 4, 5),
                       host_interface_build_number=2,
                       zwave_protocol_api_version=(4, 5, 6),
                       zwave_protocol_build_number=3,
                       application_api_version=(5, 6, 7),
                       application_build_number=4)

    def test_capabilities_get(self, rx, tx):
        rx('VERSION_CAPABILITIES_GET')
        tx('VERSION_CAPABILITIES_REPORT', zwave_software=True, command_class=True, version=True)

    def test_software_get(self, rx, tx):
        rx('VERSION_ZWAVE_SOFTWARE_GET')
        tx('VERSION_ZWAVE_SOFTWARE_REPORT',
           sdk_version=make_object(major=1, minor=2, patch=3),
           zwave_application_framework=make_object(api_version=make_object(major=2, minor=3, patch=4), build_number=1),
           host_interface=make_object(api_version=make_object(major=3, minor=4, patch=5), build_number=2),
           zwave_protocol=make_object(api_version=make_object(major=4, minor=5, patch=6), build_number=3),
           application=make_object(api_version=make_object(major=5, minor=6, patch=7), build_number=4))
