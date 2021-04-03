from ..command_class import CommandClass, command_class
from ...channel import Channel

from common import Command

from tools import visit, Object, make_object

from typing import Optional, Tuple, List


MajorMinor = Tuple[int, int]
MajorMinorPatch = Tuple[int, int, int]


@command_class('COMMAND_CLASS_VERSION', version=1)
class Version1(CommandClass):
    def __init__(
        self,
        channel: Channel,
        protocol_library_type: int,
        protocol_version: MajorMinor,
        application_version: MajorMinor
    ):
        super().__init__(channel)
        self.protocol_library_type = protocol_library_type
        self.protocol_version = protocol_version
        self.application_version = application_version

    @visit('VERSION_GET')
    def handle_get(self, command: Command, source_id: int):
        self.send_report(destination_id=source_id)

    def send_report(self, destination_id: int):
        command = self.prepare_version_report()
        self.send_command(destination_id, command)

    @visit('VERSION_COMMAND_CLASS_GET')
    def handle_command_class_get(self, command: Command, source_id: int):
        self.send_command_class_report(destination_id=source_id, class_id=command.class_id)

    def send_command_class_report(self, destination_id: int, class_id: int):
        command = self.make_command('VERSION_COMMAND_CLASS_REPORT',
                                    class_id=class_id,
                                    version=self.get_command_class_version(class_id) or 0)

        self.send_command(destination_id, command)

    def get_command_class_version(self, class_id: int) -> Optional[int]:
        for channel in self.node.channels:
            if (cc := channel.command_classes.get(class_id)) is not None:
                return cc.class_version

    def prepare_version_report(self):
        return self.make_command('VERSION_REPORT',
                                 protocol_library_type=self.protocol_library_type,
                                 protocol_version=self.to_major_minor(self.protocol_version),
                                 application_version=self.to_major_minor(self.application_version))

    @classmethod
    def to_major_minor(cls, data: MajorMinor) -> Object:
        return make_object(major=data[0], minor=data[1])


@command_class('COMMAND_CLASS_VERSION', version=2)
class Version2(Version1):
    def __init__(
        self,
        channel: Channel,
        protocol_library_type: int,
        protocol_version: MajorMinor,
        application_version: MajorMinor,
        hardware_version: int,
        firmware_versions: List[MajorMinor]
    ):
        super().__init__(channel, protocol_library_type, protocol_version, application_version)
        self.hardware_version = hardware_version
        self.firmware_versions = firmware_versions

    def prepare_version_report(self):
        command = super().prepare_version_report()
        command.hardware_version = self.hardware_version
        command.firmware_versions = [self.to_major_minor(version) for version in self.firmware_versions]
        return command


@command_class('COMMAND_CLASS_VERSION', version=3)
class Version3(Version2):
    def __init__(
        self,
        channel: Channel,
        protocol_library_type: int,
        protocol_version: MajorMinor,
        application_version: MajorMinor,
        hardware_version: int,
        firmware_versions: List[MajorMinor],
        sdk_version: Optional[MajorMinorPatch] = None,
        zwave_application_framework_api_version: Optional[MajorMinorPatch] = None,
        zwave_application_framework_build_number: Optional[int] = None,
        host_interface_api_version: Optional[MajorMinorPatch] = None,
        host_interface_build_number: Optional[int] = None,
        zwave_protocol_api_version: Optional[MajorMinorPatch] = None,
        zwave_protocol_build_number: Optional[int] = None,
        application_api_version: Optional[MajorMinorPatch] = None,
        application_build_number: Optional[int] = None
    ):
        super().__init__(channel, protocol_library_type, protocol_version, application_version, hardware_version, firmware_versions)
        self.sdk_version = sdk_version
        self.zwave_application_framework_api_version = zwave_application_framework_api_version
        self.zwave_application_framework_build_number = zwave_application_framework_build_number
        self.host_interface_api_version = host_interface_api_version
        self.host_interface_build_number = host_interface_build_number
        self.zwave_protocol_api_version = zwave_protocol_api_version
        self.zwave_protocol_build_number = zwave_protocol_build_number
        self.application_api_version = application_api_version
        self.application_build_number = application_build_number

    @visit('VERSION_CAPABILITIES_GET')
    def handle_capabilities_get(self, command: Command, source_id: int):
        self.send_capabilities_report(destination_id=source_id)

    def send_capabilities_report(self, destination_id: int):
        command = self.prepare_capabilities_report()
        self.send_command(destination_id, command)

    @visit('VERSION_ZWAVE_SOFTWARE_GET')
    def handle_zwave_software_get(self, command: Command, source_id: int):
        self.send_zwave_software_report(destination_id=source_id)

    def send_zwave_software_report(self, destination_id: int):
        if self.sdk_version is not None:
            command = self.prepare_zwave_software_report()
            self.send_command(destination_id, command)

    def prepare_capabilities_report(self):
        return self.make_command('VERSION_CAPABILITIES_REPORT',
                                 zwave_software=self.sdk_version is not None,
                                 command_class=True,
                                 version=True)

    def prepare_zwave_software_report(self):
        return self.make_command('VERSION_ZWAVE_SOFTWARE_REPORT',
                                 sdk_version=self.to_major_minor_patch(self.sdk_version),
                                 zwave_application_framework=self.to_software_info(self.zwave_application_framework_api_version,
                                                                                   self.zwave_application_framework_build_number),
                                 host_interface=self.to_software_info(self.host_interface_api_version,
                                                                      self.host_interface_build_number),
                                 zwave_protocol=self.to_software_info(self.zwave_protocol_api_version,
                                                                      self.zwave_protocol_build_number),
                                 application=self.to_software_info(self.application_api_version,
                                                                   self.application_build_number))

    @classmethod
    def to_software_info(cls, data: MajorMinorPatch, build_number: int) -> Object:
        return make_object(api_version=cls.to_major_minor_patch(data), build_number=build_number)

    @classmethod
    def to_major_minor_patch(cls, data: MajorMinorPatch) -> Object:
        return make_object(major=data[0], minor=data[1], patch=data[2])
