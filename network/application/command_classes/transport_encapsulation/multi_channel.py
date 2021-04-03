from ..command_class import CommandClass, command_class

from common import Command

from tools import visit, each_bit


@command_class('COMMAND_CLASS_MULTI_CHANNEL', version=3)
class MultiChannel3(CommandClass):
    @visit('MULTI_CHANNEL_END_POINT_GET')
    def handle_endpoint_get(self, command: Command, source_id: int):
        self.send_endpoint_report(destination_id=source_id)

    def send_endpoint_report(self, destination_id: int):
        command = self.prepare_channel_endpoint_report()
        self.send_command(destination_id, command)

    @visit('MULTI_CHANNEL_CAPABILITY_GET')
    def handle_capability_get(self, command: Command, source_id: int):
        self.send_capability_report(destination_id=source_id, endpoint=command.endpoint)

    def send_capability_report(self, destination_id: int, endpoint: int):
        command = self.prepare_capability_report(endpoint)
        self.send_command(destination_id, command)

    @visit('MULTI_CHANNEL_END_POINT_FIND')
    def handle_endpoint_find(self, command: Command, source_id: int):
        self.send_endpoint_find_report(destination_id=source_id,
                                       generic=command.generic_device_class,
                                       specific=command.specific_device_class)

    def send_endpoint_find_report(self, destination_id: int, generic: int, specific: int):
        command = self.prepare_endpoint_find_report(generic, specific)
        self.send_command(destination_id, command)

    @visit('MULTI_CHANNEL_CMD_ENCAP')
    def handle_encapsulated_command(self, command: Command, source_id: int):
        if command.bit_address:
            for channel_id in each_bit(command.destination):
                channel = self.node.channels[channel_id]
                channel.handle_command(source_id, command.command)
        else:
            channel = self.node.channels[command.destination]
            channel.handle_command(source_id, command.command)

    def send_encapsulated_command(self, destination_id: int, source_endpoint: int, command: Command):
        command = self.make_command('MULTI_CHANNEL_CMD_ENCAP',
                                    source_endpoint=source_endpoint,
                                    bit_address=False,
                                    destination=0,
                                    command=command)
        self.send_command(destination_id, command)

    def prepare_channel_endpoint_report(self) -> Command:
        prototype = self.node.channels[0]

        def key(channel):
            return channel.generic == prototype.generic and \
                   channel.specific == prototype.specific and \
                   channel.command_classes == prototype.command_classes

        identical = all(key(channel) for channel in self.node.channels[1:])

        return self.make_command('MULTI_CHANNEL_END_POINT_REPORT',
                                 dynamic=False,
                                 identical=identical,
                                 endpoints=len(self.node.channels))

    def prepare_capability_report(self, channel_id: int) -> Command:
        channel = self.node.channels[channel_id]

        return self.make_command('MULTI_CHANNEL_CAPABILITY_REPORT',
                                 dynamic=False,
                                 endpoint=channel_id,
                                 generic_device_class=channel.generic,
                                 specific_device_class=channel.specific,
                                 command_class_ids=[cc_id for cc_id in channel.command_classes if cc_id != 0x20])

    def prepare_endpoint_find_report(self, generic: int, specific: int) -> Command:
        endpoints = [channel.endpoint for channel in self.node.channels
                     if channel.generic == generic and channel.specific == specific]

        return self.make_command('MULTI_CHANNEL_END_POINT_FIND_REPORT',
                                 reports_to_follow=0,
                                 generic_device_class=generic,
                                 specific_device_class=specific,
                                 endpoints=endpoints)
