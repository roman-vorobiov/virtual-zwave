from network.protocol import make_command

from tools import make_object


COMMAND_CLASS_MANUFACTURER_SPECIFIC_1 = [
    (
        [0x72, 0x04],
        make_command(0x72, 'MANUFACTURER_SPECIFIC_GET', 1)
    ),
    (
        [0x72, 0x05, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06],
        make_command(0x72, 'MANUFACTURER_SPECIFIC_REPORT', 1,
                     manufacturer_id=0x0102,
                     product_type_id=0x0304,
                     product_id=0x0506)
    ),
    (
        [0x72, 0x06, 0x01],
        make_command(0x72, 'DEVICE_SPECIFIC_GET', 1,
                     device_id_type=0x01)
    ),
    (
        [0x72, 0x07, 0x01, 0x02, 0x03, 0x04],
        make_command(0x72, 'DEVICE_SPECIFIC_REPORT', 1,
                     device_id_type=0x01,
                     device_id_data_format=0x00,
                     device_id_data=[0x03, 0x04])
    )
]

COMMAND_CLASS_VERSION_1 = [
    (
        [0x86, 0x11],
        make_command(0x86, 'VERSION_GET', 1)
    ),
    (
        [0x86, 0x12, 0x01, 0x02, 0x03, 0x04, 0x05],
        make_command(0x86, 'VERSION_GET', 1,
                     protocol_library_type=0x01,
                     protocol_version=make_object(major=0x02, minor=0x03),
                     application_version=make_object(major=0x04, minor=0x05))
    ),
    (
        [0x86, 0x13, 0x01],
        make_command(0x86, 'VERSION_COMMAND_CLASS_GET', 1,
                     class_id=0x01)
    ),
    (
        [0x86, 0x14, 0x01, 0x02],
        make_command(0x86, 'VERSION_COMMAND_CLASS_REPORT', 1,
                     class_id=0x01,
                     version=0x02)
    )
]

COMMAND_CLASS_VERSION_2 = [
    (
        [0x86, 0x12, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x02, 0x08, 0x09, 0x0A, 0x0B],
        make_command(0x86, 'VERSION_REPORT', 2,
                     protocol_library_type=0x01,
                     protocol_version=make_object(major=0x02, minor=0x03),
                     application_version=make_object(major=0x04, minor=0x05),
                     hardware_version=0x06,
                     firmware_versions=[
                         make_object(major=0x08, minor=0x09),
                         make_object(major=0x0A, minor=0x0B)
                     ])
    )
]

COMMAND_CLASS_VERSION_3 = [
    (
        [0x86, 0x15],
        make_command(0x86, 'CAPABILITIES_GET', 3)
    ),
    (
        [0x86, 0x16, 0x05],
        make_command(0x86, 'CAPABILITIES_REPORT', 3,
                     zwave_software=True,
                     command_class=False,
                     version=True)
    ),
    (
        [0x86, 0x17],
        make_command(0x86, 'SOFTWARE_GET', 3)
    ),
    (
        [
            0x86,
            0x18,
            0x01, 0x02, 0x03,
            0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0x0C, 0x0D,
            0x0E, 0x0F, 0x10, 0x11, 0x12,
            0x13, 0x14, 0x15, 0x16, 0x17
        ],
        make_command(0x86, 'SOFTWARE_REPORT', 3,
                     sdk_version=make_object(major=0x01, minor=0x02, patch=0x03),
                     zwave_application_framework=make_object(api_version=make_object(major=0x04, minor=0x05, patch=0x06),
                                                             build_number=0x0708),
                     host=make_object(api_version=make_object(major=0x09, minor=0x0A, patch=0x0B),
                                      build_number=0x0C0D),
                     zwave_protocol=make_object(api_version=make_object(major=0x0E, minor=0x0F, patch=0x10),
                                                build_number=0x1112),
                     application=make_object(api_version=make_object(major=0x13, minor=0x14, patch=0x15),
                                             build_number=0x1617))
    )
]

COMMAND_CLASS_ZWAVEPLUS_INFO_2 = [
    (
        [0x5E, 0x01],
        make_command(0x5E, 'ZWAVEPLUS_INFO_GET', 2)
    ),
    (
        [0x5E, 0x02, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07],
        make_command(0x5E, 'ZWAVEPLUS_INFO_REPORT', 2,
                     zwave_plus_version=0x01,
                     role_type=0x02,
                     node_type=0x03,
                     installer_icon_type=0x0405,
                     user_icon_type=0x0607)
    )
]

MANAGEMENT = [
    *COMMAND_CLASS_MANUFACTURER_SPECIFIC_1,
    *COMMAND_CLASS_VERSION_1,
    *COMMAND_CLASS_VERSION_2,
    *COMMAND_CLASS_VERSION_3,
    *COMMAND_CLASS_ZWAVEPLUS_INFO_2
]
