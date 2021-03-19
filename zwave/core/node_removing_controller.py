from zwave.protocol.commands.remove_node_from_network import RemoveNodeMode, RemoveNodeStatus

from tools import Object, ReusableFuture, empty_async_generator

from asyncio import CancelledError
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .network import Network


class NodeRemovingController:
    def __init__(self, network: 'Network'):
        self.network = network
        self.node_id = ReusableFuture()

    def on_node_information_frame(self, node_id: Optional[int], node_info: Optional[Object]):
        self.node_id.set_result(node_id)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        handlers = {
            RemoveNodeMode.ANY:  self.start,
            RemoveNodeMode.STOP: self.stop
        }

        return handlers[mode]()

    async def start(self):
        yield RemoveNodeStatus.LEARN_READY, 0, None

        try:
            node_id = await self.node_id
            yield RemoveNodeStatus.NODE_FOUND, 0, None

            node_info = self.network.nodes.pop(node_id)
            yield RemoveNodeStatus.REMOVING_SLAVE, node_id, node_info

            self.network.dummy_node.remove_from_network()
            yield RemoveNodeStatus.DONE, node_id, node_info
        except CancelledError:
            pass

    @empty_async_generator
    async def stop(self):
        self.node_id.cancel()
