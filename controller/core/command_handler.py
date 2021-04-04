from .request_manager import RequestManager
from .storage import Storage
from .network_controller import NetworkController
from .library import Library

from controller.protocol import Packet, PacketVisitor
from controller.protocol.serialization import PacketSerializer

from tools import visit, log_warning

import asyncio
from typing import List


class CommandHandler(PacketVisitor):
    def __init__(
        self,
        command_serializer: PacketSerializer,
        request_manager: RequestManager,
        storage: Storage,
        library: Library,
        network_controller: NetworkController
    ):
        self.command_serializer = command_serializer
        self.request_manager = request_manager
        self.storage = storage
        self.library = library
        self.network_controller = network_controller

    def process_packet(self, packet: List[int]):
        command = self.command_serializer.from_bytes(packet)
        if (async_task := self.visit(command)) is not None:
            asyncio.create_task(async_task)

    @visit('APPLICATION_NODE_INFORMATION')
    def handle_application_node_information(self, command: Packet):
        pass

    @visit('MEMORY_GET_ID')
    def handle_memory_get_id(self, command: Packet):
        self.request_manager.send_response('MEMORY_GET_ID',
                                           home_id=self.network_controller.home_id,
                                           node_id=self.network_controller.node_id)

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
                                           node_id=self.network_controller.suc_node_id)

    @visit('SET_SUC_NODE_ID')
    def handle_set_suc_node_id(self, command: Packet):
        result = self.network_controller.set_suc_node_id(command.node_id)
        self.request_manager.send_response('SET_SUC_NODE_ID',
                                           result=result)

    @visit('ADD_NODE_TO_NETWORK')
    async def handle_add_node_to_network(self, command: Packet):
        async for status, source, node_info in self.network_controller.add_node_to_network(command.mode):
            self.request_manager.send_request('ADD_NODE_TO_NETWORK',
                                              function_id=command.function_id,
                                              status=status,
                                              source=source,
                                              node_info=node_info)

    @visit('REMOVE_NODE_FROM_NETWORK')
    async def handle_remove_node_from_network(self, command: Packet):
        async for status, source, node_info in self.network_controller.remove_node_from_network(command.mode):
            self.request_manager.send_request('REMOVE_NODE_FROM_NETWORK',
                                              function_id=command.function_id,
                                              status=status,
                                              source=source,
                                              node_info=node_info)

    @visit('GET_NODE_PROTOCOL_INFO')
    def handle_get_node_protocol_info(self, command: Packet):
        if (node_info := self.network_controller.get_node_protocol_info(command.node_id)) is not None:
            self.request_manager.send_response('GET_NODE_PROTOCOL_INFO',
                                               basic=node_info.basic,
                                               generic=node_info.generic,
                                               specific=node_info.specific)

    @visit('REQUEST_NODE_INFO')
    def handle_request_node_info(self, command: Packet):
        self.network_controller.request_node_info(command.node_id)
        self.request_manager.send_response('REQUEST_NODE_INFO',
                                           result=True)

    @visit('SEND_DATA')
    def handle_send_data(self, command: Packet):
        known_node = self.network_controller.node_infos.find(command.node_id) is not None
        self.request_manager.send_response('SEND_DATA',
                                           result=known_node)

        if not known_node:
            log_warning(f"Unknown node {command.node_id}")
            return

        async def flow():
            async for tx_status in self.network_controller.send_data(command.node_id, command.data):
                self.request_manager.send_request('SEND_DATA',
                                                  function_id=command.function_id,
                                                  tx_status=tx_status)

        return flow()

    @visit('ASSIGN_SUC_RETURN_ROUTE')
    def handle_assign_suc_return_route(self, command: Packet):
        self.request_manager.send_response('ASSIGN_SUC_RETURN_ROUTE',
                                           result=True)

        async def flow():
            async for status in self.network_controller.assign_suc_return_route(command.node_id):
                self.request_manager.send_request('ASSIGN_SUC_RETURN_ROUTE',
                                                  function_id=command.function_id,
                                                  status=status)

        return flow()

    @visit('SET_DEFAULT')
    def handle_set_default(self, command: Packet):
        self.network_controller.reset()
        self.request_manager.send_request('SET_DEFAULT',
                                          function_id=command.function_id)

    @visit('NVR_GET_VALUE')
    def handle_nvr_get_value(self, command: Packet):
        data = self.storage.get(command.offset, command.length)
        self.request_manager.send_response('NVR_GET_VALUE',
                                           data=data)

    def visit_default(self, packet: Packet, *args, **kwargs):
        log_warning(str(packet))
