from controller.protocol.commands.add_node_to_network import AddNodeMode, AddNodeStatus

from tools import Object, make_object, ReusableFuture, empty_async_generator

from asyncio import CancelledError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .network_controller import NetworkController


class NodeAddingController:
    def __init__(self, network_controller: 'NetworkController'):
        self.network_controller = network_controller
        self.node_info = ReusableFuture()
        self.new_node_id = 0

    def on_node_information_frame(self, home_id: int, node_id: int, node_info: Object):
        self.node_info.set_result((home_id, node_id, node_info))

    def add_node_to_network(self, mode: AddNodeMode):
        handlers = {
            AddNodeMode.ANY:         self.start,
            AddNodeMode.STOP:        self.stop,
            AddNodeMode.SMART_START: self.enable_smart_start
        }

        return handlers[mode]()

    async def start(self):
        yield AddNodeStatus.LEARN_READY, 0, None
        self.network_controller.broadcast_message('ADD_NODE_STARTED', {})

        try:
            old_home_id, old_node_id, node_info = await self.node_info
            yield AddNodeStatus.NODE_FOUND, 0, None

            if old_home_id == self.network_controller.home_id:
                yield AddNodeStatus.FAILED, 0, None
                return

            self.new_node_id = self.generate_node_id()
            self.network_controller.node_infos.add(self.new_node_id, make_object(
                basic=node_info.basic,
                generic=node_info.generic,
                specific=node_info.specific,
                # Controller doesn't store command classes, but this field is still required for serialization
                command_class_ids=[]
            ))
            yield AddNodeStatus.ADDING_SLAVE, self.new_node_id, node_info

            self.network_controller.send_message(old_home_id, old_node_id, 'ADD_TO_NETWORK', {
                'newNodeId': self.new_node_id
            })
            yield AddNodeStatus.PROTOCOL_DONE, self.new_node_id, None
        except CancelledError:
            pass

    async def stop(self):
        self.node_info.cancel()
        yield AddNodeStatus.DONE, self.new_node_id, None

    @empty_async_generator
    async def enable_smart_start(self):
        pass

    def generate_node_id(self) -> int:
        return max(self.network_controller.node_infos.get_node_ids(), default=self.network_controller.node_id) + 1
