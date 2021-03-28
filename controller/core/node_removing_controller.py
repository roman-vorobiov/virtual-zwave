from controller.protocol.commands.remove_node_from_network import RemoveNodeMode, RemoveNodeStatus

from tools import Object, ReusableFuture, empty_async_generator

from asyncio import CancelledError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .network_controller import NetworkController


class NodeRemovingController:
    def __init__(self, network_controller: 'NetworkController'):
        self.network_controller = network_controller
        self.node_id = ReusableFuture()

    def on_node_information_frame(self, home_id: int, node_id: int, node_info: Object):
        self.node_id.set_result((home_id, node_id, node_info))

    def remove_node_from_network(self, mode: RemoveNodeMode):
        handlers = {
            RemoveNodeMode.ANY:  self.start,
            RemoveNodeMode.STOP: self.stop
        }

        return handlers[mode]()

    async def start(self):
        yield RemoveNodeStatus.LEARN_READY, 0, None
        self.network_controller.broadcast_message('REMOVE_NODE_STARTED', {})

        try:
            home_id, node_id, _ = await self.node_id
            yield RemoveNodeStatus.NODE_FOUND, 0, None

            node_info = self.network_controller.nodes.pop(node_id)
            yield RemoveNodeStatus.REMOVING_SLAVE, node_id, node_info

            self.network_controller.send_message(home_id, node_id, 'REMOVE_FROM_NETWORK', {})
            yield RemoveNodeStatus.DONE, node_id, node_info
        except CancelledError:
            pass

    @empty_async_generator
    async def stop(self):
        self.node_id.cancel()
