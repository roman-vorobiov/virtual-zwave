from .resources import Resources
from .device import Device
from .host import Host
from .request_manager import RequestManager
from .frame_handler import FrameHandler
from .command_handler import CommandHandler
from .network_event_handler import NetworkEventHandler
from .library import Library
from .network_controller import NetworkController
from .storage import Storage

from zwave.protocol.serialization import PacketSerializer, CommandClassSerializer

from common import NetworkImpl

from tools import load_yaml
from tools.websockets import NetworkConnection

from typing import List


def make_packet_serializer(schema_path: str) -> PacketSerializer:
    return PacketSerializer(load_yaml(schema_path))


def make_command_class_serializer(*schema_paths: str) -> CommandClassSerializer:
    data = {}
    for schema_path in schema_paths:
        data.update(load_yaml(schema_path))

    return CommandClassSerializer(data)


class Core:
    def __init__(self, device: Device, connection: NetworkConnection):
        self.frame_serializer = make_packet_serializer("zwave/protocol/frames/frames.yaml")
        self.requests_from_host_serializer = make_packet_serializer("zwave/protocol/commands/requests_from_host.yaml")
        self.requests_to_host_serializer = make_packet_serializer("zwave/protocol/commands/requests_to_host.yaml")
        self.responses_to_host_serializer = make_packet_serializer("zwave/protocol/commands/responses_to_host.yaml")
        self.command_class_serializer = make_command_class_serializer(
            "zwave/protocol/command_classes/management.yaml",
            "zwave/protocol/command_classes/application.yaml"
        )

        self.network = NetworkImpl(
            connection=connection
        )

        self.host = Host(
            frame_serializer=self.frame_serializer,
            device=device
        )
        self.request_manager = RequestManager(
            request_serializer=self.requests_to_host_serializer,
            response_serializer=self.responses_to_host_serializer,
            host=self.host
        )

        self.resources = Resources()
        self.storage = Storage(
            resources=self.resources
        )
        self.library = Library(
            resources=self.resources
        )
        self.network_controller = NetworkController(
            command_class_serializer=self.command_class_serializer,
            request_manager=self.request_manager,
            network=self.network
        )

        self.command_handler = CommandHandler(
            command_serializer=self.requests_from_host_serializer,
            request_manager=self.request_manager,
            storage=self.storage,
            library=self.library,
            network_controller=self.network_controller
        )
        self.frame_handler = FrameHandler(
            frame_serializer=self.frame_serializer,
            host=self.host,
            command_handler=self.command_handler
        )

        self.network_event_handler = NetworkEventHandler(
            network=self.network,
            network_controller=self.network_controller
        )

    def process_packet(self, packet: List[int]):
        self.frame_handler.process_packet(packet)

    def process_message(self, message: str):
        self.network_event_handler.process_message(message)
