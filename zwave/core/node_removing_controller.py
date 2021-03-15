from zwave.protocol.commands.remove_node_from_network import RemoveNodeMode, RemoveNodeStatus

from tools import Object, empty_async_generator

from asyncio import Future, CancelledError
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .network import Network


class NodeRemovingController:
    def __init__(self, network: 'Network'):
        self.network = network
        self.node_id = Future()

    def reset(self):
        self.node_id = Future()

    def on_node_information_frame(self, node_id: Optional[int], node_info: Optional[Object]):
        self.node_id.set_result(node_id)

    def remove_node_from_network(self, mode: RemoveNodeMode):
        handlers = {
            RemoveNodeMode.ANY:  self.start,
            RemoveNodeMode.STOP: self.stop
        }

        return handlers[mode]()

    async def start(self):
        self.reset()
        yield RemoveNodeStatus.LEARN_READY, 0, None

        # if (node_id := next(iter(self.network.nodes), None)) is not None:
        #     self.on_node_information_frame(node_id, self.network.nodes[node_id])

        try:
            await self.node_id
            yield RemoveNodeStatus.NODE_FOUND, 0, None

            node_info = self.network.nodes.pop(self.node_id.result())
            yield RemoveNodeStatus.REMOVING_SLAVE, self.node_id.result(), node_info

            yield RemoveNodeStatus.DONE, self.node_id.result(), node_info
        except CancelledError:
            pass

    @empty_async_generator
    async def stop(self):
        self.node_id.cancel()
