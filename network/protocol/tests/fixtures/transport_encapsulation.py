from network.protocol import make_command

from tools import make_object


COMMAND_CLASS_MULTI_CHANNEL_3 = [
    (
        [0x60, 0x07],
        make_command(0x60, 'MULTI_CHANNEL_END_POINT_GET', 3)
    ),
    (
        [0x60, 0x08, 0x80, 0x01],
        make_command(0x60, 'MULTI_CHANNEL_END_POINT_REPORT', 3,
                     dynamic=True,
                     identical=False,
                     endpoints=0x01)
    ),
    (
        [0x60, 0x09, 0x01],
        make_command(0x60, 'MULTI_CHANNEL_CAPABILITY_GET', 3,
                     endpoint=0x01)
    ),
    (
        [0x60, 0x0A, 0x81, 0x01, 0x02, 0x03, 0x04],
        make_command(0x60, 'MULTI_CHANNEL_CAPABILITY_REPORT', 3,
                     dynamic=True,
                     endpoint=0x01,
                     generic_device_class=0x01,
                     specific_device_class=0x02,
                     command_class_ids=[0x03, 0x04])
    ),
    (
        [0x60, 0x0B, 0x01, 0x02],
        make_command(0x60, 'MULTI_CHANNEL_END_POINT_FIND', 3,
                     generic_device_class=0x01,
                     specific_device_class=0x02)
    ),
    (
        [0x60, 0x0C, 0x01, 0x02, 0x03, 0x04, 0x05],
        make_command(0x60, 'MULTI_CHANNEL_END_POINT_FIND_REPORT', 3,
                     reports_to_follow=0x01,
                     generic_device_class=0x02,
                     specific_device_class=0x03,
                     endpoints=[0x04, 0x05])
    ),
    (
        [0x60, 0x0D, 0x01, 0x02, 0x03, 0x04],
        make_command(0x60, 'MULTI_CHANNEL_CMD_ENCAP', 3,
                     source_endpoint=0x01,
                     bit_address=False,
                     destination=0x02,
                     command=[0x03, 0x04])
    )
]

COMMAND_CLASS_MULTI_CMD_1 = [
    (
        [0x8F, 0x01, 0x02, 0x03, 0x01, 0x02, 0x03, 0x02, 0x04, 0x05],
        make_command(0x60, 'MULTI_CMD_ENCAP', 1,
                     commands=[
                         make_object(command=[0x01, 0x02, 0x03]),
                         make_object(command=[0x04, 0x05])
                     ])
    ),
]

TRANSPORT_ENCAPSULATION = [
    *COMMAND_CLASS_MULTI_CHANNEL_3,
    *COMMAND_CLASS_MULTI_CMD_1
]
