from zwave.protocol.commands.add_node_to_network import AddNodeMode, AddNodeStatus

from tools import Object, empty_async_generator

from asyncio import Future, CancelledError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .network import Network


class NodeAddingController:
    def __init__(self, network: 'Network'):
        self.network = network
        self.node_info = Future()
        self.new_node_id = 0

    def reset(self):
        self.node_info = Future()
        self.new_node_id = 0

    def on_node_information_frame(self, node_info: Object):
        self.node_info.set_result(node_info)

    def add_node_to_network(self, mode: AddNodeMode):
        handlers = {
            AddNodeMode.ANY:         self.start,
            AddNodeMode.STOP:        self.stop,
            AddNodeMode.SMART_START: self.enable_smart_start
        }

        return handlers[mode]()

    async def start(self):
        self.reset()
        yield AddNodeStatus.LEARN_READY, 0, None

        # if len(self.network.nodes) == 0:
        #     self.on_node_information_frame(Object(basic=0x04,
        #                                           generic=0x01,
        #                                           specific=0x01,
        #                                           command_class_ids=[0x5E, 0x72, 0x20]))

        try:
            await self.node_info
            yield AddNodeStatus.NODE_FOUND, 0, None

            self.new_node_id = self.generate_node_id()
            yield AddNodeStatus.ADDING_SLAVE, self.new_node_id, self.node_info.result()

            self.network.nodes[self.new_node_id] = self.node_info.result()
            yield AddNodeStatus.PROTOCOL_DONE, self.new_node_id, None
        except CancelledError:
            pass

    async def stop(self):
        self.node_info.cancel()
        yield AddNodeStatus.DONE, self.new_node_id, None

    @empty_async_generator
    async def enable_smart_start(self):
        pass

    def generate_node_id(self):
        # return next(reversed(self.network.nodes.keys()), self.network.node_id) + 1
        if len(self.network.nodes):
            return next(reversed(self.network.nodes.keys())) + 1
        else:
            return self.network.node_id + 1
