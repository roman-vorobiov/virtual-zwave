from zwave.protocol import Packet

import random


class Network:
    def __init__(self):
        self.home_id = 0
        self.node_id = 1
        self.suc_id = self.node_id

        self.reset()

    def reset(self):
        self.home_id = random.randint(0xC0000000, 0xFFFFFFFE)

    def handle_add_node_to_network_command(self, command: Packet):
        # Todo
        pass

    def handle_remove_node_from_network_command(self, command: Packet):
        # Todo
        pass
