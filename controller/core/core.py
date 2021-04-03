from .controller import Controller
from .host import Host
from .request_manager import RequestManager
from .frame_handler import FrameHandler
from .command_handler import CommandHandler
from .network_event_handler import NetworkEventHandler
from .library import Library
from .network_controller import NetworkController
from .storage import Storage

from controller.model.tinydb import DatabaseProvider

from controller.protocol.serialization import PacketSerializer, CommandClassSerializer

from common import RemoteInterfaceImpl

from tools import Resources, load_yaml
from tools.websockets import RemoteConnection

import os.path
from typing import List


def make_packet_serializer(schema_path: str) -> PacketSerializer:
    return PacketSerializer(load_yaml(os.path.join("controller", "protocol", schema_path)))


def make_command_class_serializer(*schema_paths: str) -> CommandClassSerializer:
    data = {}
    for schema_path in schema_paths:
        data.update(load_yaml(os.path.join("controller", "protocol", schema_path)))

    return CommandClassSerializer(data)


class Core:
    def __init__(self, device: Controller, connection: RemoteConnection):
        self.config = Resources("controller/resources/config.yaml")

        self.frame_serializer = make_packet_serializer("frames/frames.yaml")
        self.requests_from_host_serializer = make_packet_serializer("commands/requests_from_host.yaml")
        self.requests_to_host_serializer = make_packet_serializer("commands/requests_to_host.yaml")
        self.responses_to_host_serializer = make_packet_serializer("commands/responses_to_host.yaml")
        self.command_class_serializer = make_command_class_serializer("command_classes/management.yaml",
                                                                      "command_classes/transport_encapsulation.yaml",
                                                                      "command_classes/application.yaml")

        self.repository_provider = DatabaseProvider()
        self.state = self.repository_provider.get_state()
        self.node_infos = self.repository_provider.get_node_infos()

        self.network = RemoteInterfaceImpl(
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

        self.storage = Storage(
            config=self.config
        )
        self.library = Library(
            config=self.config
        )
        self.network_controller = NetworkController(
            command_class_serializer=self.command_class_serializer,
            state=self.state,
            node_infos=self.node_infos,
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
            network_controller=self.network_controller,
            request_manager=self.request_manager
        )

    def process_packet(self, packet: List[int]):
        self.frame_handler.process_packet(packet)

    def process_message(self, message: str):
        self.network_event_handler.process_message(message)
