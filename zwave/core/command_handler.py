from .request_manager import RequestManager
from .storage import Storage
from .network import Network
from .library import Library

from zwave.protocol import Packet, PacketVisitor
from zwave.protocol.serialization import PacketSerializer

from tools import visit, log_warning

from typing import List


class CommandHandler(PacketVisitor):
    def __init__(
        self,
        command_serializer: PacketSerializer,
        request_manager: RequestManager,
        storage: Storage,
        library: Library,
        network: Network
    ):
        self.command_serializer = command_serializer
        self.request_manager = request_manager
        self.storage = storage
        self.library = library
        self.network = network

    def process_packet(self, packet: List[int]):
        command = self.command_serializer.from_bytes(packet)
        self.visit(command)

    @visit('APPLICATION_NODE_INFORMATION')
    def handle_application_node_information(self, command: Packet):
        pass

    @visit('MEMORY_GET_ID')
    def handle_memory_get_id(self, command: Packet):
        self.request_manager.send_response('MEMORY_GET_ID',
                                           home_id=self.network.home_id,
                                           node_id=self.network.node_id)

    @visit('VERSION')
    def handle_version(self, command: Packet):
        self.request_manager.send_response('VERSION',
                                           buffer=self.library.version,
                                           library_type=self.library.library_type)

    @visit('SET_LISTEN_BEFORE_TALK_THRESHOLD')
    def handle_set_listen_before_talk_threshold(self, command: Packet):
        self.request_manager.send_response('SET_LISTEN_BEFORE_TALK_THRESHOLD',
                                           result=True)

    @visit('GET_SUC_NODE_ID')
    def handle_get_suc_node_id(self, command: Packet):
        self.request_manager.send_response('GET_SUC_NODE_ID',
                                           node_id=self.network.suc_id)

    @visit('SET_SUC_NODE_ID')
    def handle_set_suc_node_id(self, command: Packet):
        result = self.network.set_suc_node_id(command.node_id)
        self.request_manager.send_response('SET_SUC_NODE_ID',
                                           result=result)

    @visit('ADD_NODE_TO_NETWORK')
    def handle_add_node_to_network(self, command: Packet):
        self.network.handle_add_node_to_network_command(command)

    @visit('REMOVE_NODE_FROM_NETWORK')
    def handle_remove_node_from_network(self, command: Packet):
        self.network.handle_remove_node_from_network_command(command)

    @visit('SET_DEFAULT')
    def handle_set_default(self, command: Packet):
        self.network.reset()
        self.request_manager.send_request('SET_DEFAULT',
                                          function_id=command.function_id)

    @visit('NVR_GET_VALUE')
    def handle_nvr_get_value(self, command: Packet):
        data = self.storage.get(command.offset, command.length)
        self.request_manager.send_response('NVR_GET_VALUE',
                                           data=data)

    def visit_default(self, packet: Packet, *args, **kwargs):
        log_warning(f"{packet.name} {packet.fields}")
