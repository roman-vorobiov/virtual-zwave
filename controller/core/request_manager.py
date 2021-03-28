from .host import Host

from controller.protocol import make_packet
from controller.protocol.frames.data import FrameType
from controller.protocol.serialization import PacketSerializer


class RequestManager:
    def __init__(self, request_serializer: PacketSerializer, response_serializer: PacketSerializer, host: Host):
        self.request_serializer = request_serializer
        self.response_serializer = response_serializer
        self.host = host

    def send_request(self, name: str, **kwargs):
        command = make_packet(name, **kwargs)
        data = self.request_serializer.to_bytes(command)
        self.host.send_data(FrameType.REQ, data)

    def send_response(self, name: str, **kwargs):
        command = make_packet(name, **kwargs)
        data = self.response_serializer.to_bytes(command)
        self.host.send_data(FrameType.RES, data)
