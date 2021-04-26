from ..command_class import CommandClass, command_class
from ...request_context import Context

from network.protocol import Command

from tools import Object, make_object, visit, each_bit, create_mask, RangeIterator

from typing import List, Tuple


def get_channels(destination: Object) -> List[int]:
    if destination.bit_address:
        return list(each_bit(destination.endpoint, start=1))
    else:
        return [destination.endpoint]


@command_class('COMMAND_CLASS_MULTI_CHANNEL_ASSOCIATION', version=2)
class MultiChannelAssociation2(CommandClass):
    @visit('MULTI_CHANNEL_ASSOCIATION_SET')
    def handle_set(self, command: Command, context: Context):
        for node_id in command.node_ids:
            self.channel.associations.subscribe(command.group_id, node_id)

        for destination in command.multi_channel_destinations:
            self.channel.associations.subscribe(command.group_id, destination.node_id, get_channels(destination))

        self.channel.on_state_change()

    @visit('MULTI_CHANNEL_ASSOCIATION_GET')
    def handle_get(self, command: Command, context: Context):
        self.send_report(context, group_id=command.group_id)

    @visit('MULTI_CHANNEL_ASSOCIATION_REMOVE')
    def handle_remove(self, command: Command, context: Context):
        if command.group_id == 0:
            self.remove_associations_from_all_groups(command.node_ids, command.multi_channel_destinations)
        else:
            self.remove_associations_from_group(command.group_id, command.node_ids, command.multi_channel_destinations)

        self.channel.on_state_change()

    @visit('MULTI_CHANNEL_ASSOCIATION_GROUPINGS_GET')
    def handle_groupings_get(self, command: Command, context: Context):
        self.send_groupings_report(context)

    def send_report(self, context: Context, group_id: int):
        node_ids, multi_channel_destinations = self.get_destinations(group_id)

        self.send_command(context, 'MULTI_CHANNEL_ASSOCIATION_REPORT',
                          group_id=group_id,
                          max_nodes_supported=0xFF,
                          reports_to_follow=0,
                          node_ids=node_ids,
                          multi_channel_destinations=multi_channel_destinations)

    def send_groupings_report(self, context: Context):
        self.send_command(context, 'MULTI_CHANNEL_ASSOCIATION_GROUPINGS_REPORT',
                          supported_groups=len(self.channel.associations.groups))

    def get_destinations(self, group_id: int) -> Tuple[List[int], List[Object]]:
        node_ids = []
        multi_channel_destinations = []
        for node_id, endpoints in self.channel.associations.get_destinations(group_id):
            # Note: endpoints are sorted
            it = RangeIterator(endpoints)

            # If there's a 0 endpoint, add to node_ids
            for _ in it.takewhile(lambda channel: channel == 0, peek_last=True):
                node_ids.append(node_id)

            # Add endpoints 1 to 7 into a single destination via bitmask
            if (mask := create_mask(it.takewhile(lambda channel: channel <= 7, peek_last=True), start=1)) != 0:
                multi_channel_destinations.append(make_object(node_id=node_id, endpoint=mask, bit_address=True))

            # Add the rest of endpoints as separate destinations
            multi_channel_destinations.extend(make_object(node_id=node_id, endpoint=endpoint, bit_address=False)
                                              for endpoint in it)

        return node_ids, multi_channel_destinations

    def remove_associations_from_group(self, group_id: int, node_ids: List[int], multi_channel_destinations: List[Object]):
        if len(node_ids) == 0 and len(multi_channel_destinations) == 0:
            self.channel.associations.clear_association_in_group(group_id)
        else:
            for node_id in node_ids:
                self.channel.associations.unsubscribe(group_id, node_id)

            for destination in multi_channel_destinations:
                self.channel.associations.unsubscribe(group_id, destination.node_id, get_channels(destination))

    def remove_associations_from_all_groups(self, node_ids: List[int], multi_channel_destinations: List[Object]):
        if len(node_ids) == 0 and len(multi_channel_destinations) == 0:
            self.channel.associations.clear_all()
        else:
            for node_id in node_ids:
                self.channel.associations.unsubscribe_from_all(node_id)

            for destination in multi_channel_destinations:
                self.channel.associations.unsubscribe_from_all(destination.node_id, get_channels(destination))
