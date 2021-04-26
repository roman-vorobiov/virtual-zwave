from ..command_class import CommandClass, command_class
from ...request_context import Context

from network.protocol import Command

from tools import visit, make_object


@command_class('COMMAND_CLASS_ASSOCIATION_GRP_INFO', version=1)
class AssociationGroupInfo1(CommandClass):
    @visit('ASSOCIATION_GROUP_NAME_GET')
    def handle_group_name_get(self, command: Command, context: Context):
        self.send_group_name_report(context, group_id=command.group_id)

    @visit('ASSOCIATION_GROUP_INFO_GET')
    def handle_group_info_get(self, command: Command, context: Context):
        if command.list_mode:
            self.send_group_info_report_all(context)
        else:
            self.send_group_info_report_single(context, group_id=command.group_id)

    @visit('ASSOCIATION_GROUP_COMMAND_LIST_GET')
    def handle_group_command_list_get(self, command: Command, context: Context):
        self.send_group_command_list_report(context, group_id=command.group_id)

    def send_group_name_report(self, context: Context, group_id: int):
        self.send_command(context, 'ASSOCIATION_GROUP_NAME_REPORT',
                          group_id=group_id,
                          name=self.channel.associations.get_group(group_id).name)

    def send_group_info_report_single(self, context: Context, group_id: int):
        self.send_command(context, 'ASSOCIATION_GROUP_INFO_REPORT',
                          list_mode=False,
                          dynamic_info=False,
                          groups=[self.get_group_info(group_id)])

    def send_group_info_report_all(self, context: Context):
        self.send_command(context, 'ASSOCIATION_GROUP_INFO_REPORT',
                          list_mode=True,
                          dynamic_info=False,
                          groups=[self.get_group_info(group_id) for group_id in self.channel.associations.group_ids])

    def send_group_command_list_report(self, context: Context, group_id: int):
        group = self.channel.associations.get_group(group_id)
        commands = [make_object(class_id=class_id, command_id=command_id) for class_id, command_id in group.commands]

        self.send_command(context, 'ASSOCIATION_GROUP_COMMAND_LIST_REPORT', group_id=group_id, commands=commands)

    def get_group_info(self, group_id: int):
        group = self.channel.associations.get_group(group_id)
        return make_object(group_id=group_id,
                           profile=make_object(generic=group.profile[0], specific=group.profile[1]))


@command_class('COMMAND_CLASS_ASSOCIATION_GRP_INFO', version=2)
class AssociationGroupInfo2(AssociationGroupInfo1):
    pass


@command_class('COMMAND_CLASS_ASSOCIATION_GRP_INFO', version=3)
class AssociationGroupInfo3(AssociationGroupInfo2):
    pass
