from .host import Host, DataFrameType

from zwave.protocol import Packet
from zwave.protocol.serialization import PacketSerializer


class RequestManager:
    def __init__(self, request_serializer: PacketSerializer, response_serializer: PacketSerializer, host: Host):
        self.request_serializer = request_serializer
        self.response_serializer = response_serializer
        self.host = host

    def send_request(self, name: str, **kwargs):
        command = Packet(name, **kwargs)
        data = self.request_serializer.to_bytes(command)
        self.host.send_data(DataFrameType.REQ, data)

    def send_response(self, name: str, **kwargs):
        command = Packet(name, **kwargs)
        data = self.response_serializer.to_bytes(command)
        self.host.send_data(DataFrameType.RES, data)
