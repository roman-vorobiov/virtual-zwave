from controller.protocol.commands.send_data import TransmitStatus

import asyncio
from asyncio import Future
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .network_controller import NetworkController


class SendDataController:
    # Note: in real Z-Wave chip the timeout is around 7s
    # but here we assume if the response is not received instantly, the node is unreachable
    TIMEOUT_SECONDS = 1

    def __init__(self, network_controller: 'NetworkController'):
        self.network_controller = network_controller
        self.ack: Dict[int, Future] = {}

    async def send_data(self, destination_node_id: int, command: List[int]):
        self.ack[destination_node_id] = Future()

        self.network_controller.send_message_in_current_network(destination_node_id, 'APPLICATION_COMMAND', {
            'command': command
        })

        try:
            await asyncio.wait_for(self.ack[destination_node_id], timeout=self.TIMEOUT_SECONDS)
            yield TransmitStatus.OK
        except asyncio.TimeoutError:
            yield TransmitStatus.NO_ACK
        finally:
            del self.ack[destination_node_id]

    def on_ack(self, node_id: int):
        if (ack := self.ack.get(node_id)) is not None:
            ack.set_result(True)
