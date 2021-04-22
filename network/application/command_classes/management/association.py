from ..command_class import CommandClass, command_class
from ...request_context import Context

from network.protocol import Command

from tools import visit, log_warning

from typing import List


@command_class('COMMAND_CLASS_ASSOCIATION', version=1)
class Association1(CommandClass):
    @visit('ASSOCIATION_SET')
    def handle_set(self, command: Command, context: Context):
        for node_id in command.node_ids:
            self.channel.associations.subscribe(command.group_id, node_id)

    @visit('ASSOCIATION_GET')
    def handle_get(self, command: Command, context: Context):
        self.send_report(context, group_id=command.group_id)

    @visit('ASSOCIATION_REMOVE')
    def handle_remove(self, command: Command, context: Context):
        if command.group_id == 0:
            self.remove_associations_from_all_groups(command.node_ids)
        else:
            self.remove_associations_from_group(command.group_id, command.node_ids)

    @visit('ASSOCIATION_GROUPINGS_GET')
    def handle_groupings_get(self, command: Command, context: Context):
        self.send_groupings_report(context)

    def send_report(self, context: Context, group_id: int):
        self.send_command(context, 'ASSOCIATION_REPORT',
                          group_id=group_id,
                          max_nodes_supported=0xFF,
                          reports_to_follow=0,
                          node_ids=self.channel.associations.get_destinations(group_id))

    def send_groupings_report(self, context: Context):
        self.send_command(context, 'ASSOCIATION_GROUPINGS_REPORT',
                          supported_groups=len(self.channel.associations.groups))

    def remove_associations_from_group(self, group_id: int, node_ids: List[int]):
        if len(node_ids) == 0:
            self.channel.associations.clear_association_in_group(group_id)
        else:
            for node_id in node_ids:
                self.channel.associations.unsubscribe(group_id, node_id)

    def remove_associations_from_all_groups(self, node_ids: List[int]):
        log_warning("Removing nodes from all association groups is not supported by COMMAND_CLASS_ASSOCIATION v1")


@command_class('COMMAND_CLASS_ASSOCIATION', version=2)
class Association2(Association1):
    @visit('ASSOCIATION_SPECIFIC_GROUP_GET')
    def handle_specific_group_get(self, command: Command, context: Context):
        self.send_specific_group_report(context)

    def send_specific_group_report(self, context: Context):
        # Unsupported
        self.send_command(context, 'ASSOCIATION_SPECIFIC_GROUP_REPORT', group_id=0)

    def remove_associations_from_all_groups(self, node_ids: List[int]):
        if len(node_ids) == 0:
            self.channel.associations.clear_all()
        else:
            for node_id in node_ids:
                self.channel.associations.unsubscribe_from_all(node_id)
