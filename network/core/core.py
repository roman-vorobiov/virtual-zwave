from .network_event_handler import NetworkEventHandler
from .command_handler import CommandHandler

from network.application import Node, create_node

from common import Network, NetworkImpl

from tools.websockets import NetworkConnection


def make_dummy_node(network: Network) -> Node:
    return create_node(
        network,

        basic=0x04,
        generic=0x01,
        specific=0x01,

        manufacturer_id=1,
        product_type_id=2,
        product_id=3,

        role_type=0x05,
        installer_icon_type=0x0700,
        user_icon_type=0x0700
    )


class Core:
    def __init__(self, connection: NetworkConnection):
        self.network = NetworkImpl(
            connection=connection
        )

        # Todo
        self.dummy_node = make_dummy_node(self.network)

        self.command_handler = CommandHandler(
            network=self.network,
            dummy_node=self.dummy_node
        )

        self.network_event_handler = NetworkEventHandler(
            network=self.network,
            dummy_node=self.dummy_node
        )

    def process_command(self, command: str):
        self.command_handler.handle_command(command)

    def process_message(self, message: str):
        self.network_event_handler.handle_message(message)
