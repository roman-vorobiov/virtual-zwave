from controller.protocol import PacketSerializer, make_packet

from tools import make_object, load_yaml

import pytest


@pytest.fixture(scope='session')
def frame_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/frames/frames.yaml"))


@pytest.fixture(scope='session')
def requests_from_host_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/commands/requests_from_host.yaml"))


@pytest.fixture(scope='session')
def requests_to_host_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/commands/requests_to_host.yaml"))


@pytest.fixture(scope='session')
def responses_to_host_serializer():
    yield PacketSerializer(load_yaml("controller/protocol/commands/responses_to_host.yaml"))


@pytest.mark.parametrize("data,expected", [
    ([0x06], make_packet('ACK')),
    ([0x15], make_packet('NAK')),
    ([0x18], make_packet('CAN')),
    (
        [0x01, 0x04, 0x02, 0x03, 0x04, 0x05],
        make_packet('Data', type=0x02, command=[0x03, 0x04], checksum=0x05)
    )
])
def test_frame_serialization(frame_serializer, data, expected):
    packet = frame_serializer.from_bytes(data)
    assert packet == expected
    assert frame_serializer.to_bytes(packet) == data


@pytest.mark.parametrize("data,expected", [
    (
        [0x03, 0x01, 0x02, 0x03, 0x04, 0x05],
        make_packet('APPLICATION_NODE_INFORMATION',
                    device_options=0x01,
                    generic=0x02,
                    specific=0x03,
                    command_class_ids=[0x04, 0x05])
    ),
    (
        [0x13, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06],
        make_packet('SEND_DATA', node_id=0x01, data=[0x03, 0x04], tx_options=0x05, function_id=0x06)
    ),
    (
        [0x15],
        make_packet('VERSION')
    ),
    (
        [0x20],
        make_packet('MEMORY_GET_ID')
    ),
    (
        [0x28, 0x01, 0x02],
        make_packet('NVR_GET_VALUE', offset=0x01, length=0x02)
    ),
    (
        [0x3C, 0x01, 0x02],
        make_packet('SET_LISTEN_BEFORE_TALK_THRESHOLD', channel=0x01, threshold=0x02)
    ),
    (
        [0x41, 0x01],
        make_packet('GET_NODE_PROTOCOL_INFO', node_id=0x01)
    ),
    (
        [0x42, 0x01],
        make_packet('SET_DEFAULT', function_id=0x01)
    ),
    (
        [0x4A, 0x01, 0x02],
        make_packet('ADD_NODE_TO_NETWORK', mode=0x01, options=0x00, function_id=0x02)
    ),
    (
        [0x4B, 0x01, 0x02],
        make_packet('REMOVE_NODE_FROM_NETWORK', mode=0x01, options=0x00, function_id=0x02)
    ),
    (
        [0x50, 0x01, 0x02],
        make_packet('SET_LEARN_MODE', mode=0x01, function_id=0x02)
    ),
    (
        [0x51, 0x01, 0x02, 0x02],
        make_packet('ASSIGN_SUC_RETURN_ROUTE', node_id=0x01, function_id=0x02)
    ),
    (
        [0x54, 0x01, 0x02, 0x03, 0x04, 0x05],
        make_packet('SET_SUC_NODE_ID',
                    node_id=0x01,
                    suc_state=0x02,
                    tx_option=0x03,
                    capabilities=0x04,
                    function_id=0x05)
    ),
    (
        [0x56],
        make_packet('GET_SUC_NODE_ID')
    ),
    (
        [0x60, 0x01],
        make_packet('REQUEST_NODE_INFO', node_id=0x01)
    )
])
def test_requests_from_host_serialization(requests_from_host_serializer, data, expected):
    packet = requests_from_host_serializer.from_bytes(data)
    assert packet == expected
    assert requests_from_host_serializer.to_bytes(packet) == data


@pytest.mark.parametrize("data,expected", [
    (
        [0x04, 0x05, 0x01, 0x02, 0x03, 0x04],
        make_packet('APPLICATION_COMMAND_HANDLER',
                    rx_status=0x01,
                    rx_type=0x04,
                    source_node=0x01,
                    command=[0x03, 0x04])
    ),
    (
        [0x13, 0x01, 0x02],
        make_packet('SEND_DATA', function_id=0x01, tx_status=0x02)
    ),
    (
        [0x42, 0x01],
        make_packet('SET_DEFAULT', function_id=0x01)
    ),
    (
        [0x49, 0x01, 0x02, 0x05, 0x04, 0x05, 0x06, 0x07, 0x08],
        make_packet('APPLICATION_SLAVE_UPDATE',
                    status=0x01,
                    node_id=0x02,
                    node_info=make_object(basic=0x04,
                                          generic=0x05,
                                          specific=0x06,
                                          command_class_ids=[0x07, 0x08]))
    ),
    (
        [0x4A, 0x00, 0x01, 0x02, 0x05, 0x04, 0x05, 0x06, 0x07, 0x08],
        make_packet('ADD_NODE_TO_NETWORK',
                    function_id=0x00,
                    status=0x01,
                    source=0x02,
                    node_info=make_object(basic=0x04,
                                          generic=0x05,
                                          specific=0x06,
                                          command_class_ids=[0x07, 0x08]))
    ),
    (
        [0x4B, 0x00, 0x01, 0x02, 0x05, 0x04, 0x05, 0x06, 0x07, 0x08],
        make_packet('REMOVE_NODE_FROM_NETWORK',
                    function_id=0x00,
                    status=0x01,
                    source=0x02,
                    node_info=make_object(basic=0x04,
                                          generic=0x05,
                                          specific=0x06,
                                          command_class_ids=[0x07, 0x08]))
    ),
    (
        [0x50, 0x00, 0x01, 0x02, 0x05, 0x04, 0x05, 0x06, 0x07, 0x08],
        make_packet('SET_LEARN_MODE',
                    function_id=0x00,
                    status=0x01,
                    source=0x02,
                    node_info=make_object(basic=0x04,
                                          generic=0x05,
                                          specific=0x06,
                                          command_class_ids=[0x07, 0x08]))
    ),
    (
        [0x51, 0x01, 0x02],
        make_packet('ASSIGN_SUC_RETURN_ROUTE', function_id=0x01, status=0x02)
    ),
    (
        [0x54, 0x01, 0x02],
        make_packet('SET_SUC_NODE_ID', function_id=0x01, tx_status=0x02)
    ),
])
def test_requests_to_host_serialization(requests_to_host_serializer, data, expected):
    packet = requests_to_host_serializer.from_bytes(data)
    assert packet == expected
    assert requests_to_host_serializer.to_bytes(packet) == data


@pytest.mark.parametrize("data,expected", [
    (
        [0x13, 0x01],
        make_packet('SEND_DATA', result=True)
    ),
    (
        [0x15, *b"hello\0", 0x01],
        make_packet('VERSION', buffer="hello", library_type=0x01)
    ),
    (
        [0x20, 0x01, 0x02, 0x03, 0x04, 0x05],
        make_packet('MEMORY_GET_ID', home_id=0x01020304, node_id=0x05)
    ),
    (
        [0x28, 0x01, 0x02],
        make_packet('NVR_GET_VALUE', data=[0x01, 0x02])
    ),
    (
        [0x3C, 0x01],
        make_packet('SET_LISTEN_BEFORE_TALK_THRESHOLD', result=True)
    ),
    (
        [0x41, 0x53, 0xDC, 0x01, 0x02, 0x03, 0x04],
        make_packet('GET_NODE_PROTOCOL_INFO', basic=0x02, generic=0x03, specific=0x04)
    ),
    (
        [0x50, 0x01],
        make_packet('SET_LEARN_MODE', result=True)
    ),
    (
        [0x51, 0x01],
        make_packet('ASSIGN_SUC_RETURN_ROUTE', result=True)
    ),
    (
        [0x54, 0x01],
        make_packet('SET_SUC_NODE_ID', result=True)
    ),
    (
        [0x56, 0x01],
        make_packet('GET_SUC_NODE_ID', node_id=0x01)
    ),
    (
        [0x60, 0x01],
        make_packet('REQUEST_NODE_INFO', result=True)
    ),
])
def test_responses_to_host_serialization(responses_to_host_serializer, data, expected):
    packet = responses_to_host_serializer.from_bytes(data)
    assert packet == expected
    assert responses_to_host_serializer.to_bytes(packet) == data
