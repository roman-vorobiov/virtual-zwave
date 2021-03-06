from ..command_class import CommandClass, command_class
from ...channel import Channel
from ...request_context import Context

from network.protocol import Command

from tools import visit, each_bit

from typing import List, Iterator


@command_class('COMMAND_CLASS_MULTI_CHANNEL', version=3)
class MultiChannel3(CommandClass):
    @visit('MULTI_CHANNEL_END_POINT_GET')
    def handle_endpoint_get(self, command: Command, context: Context):
        self.send_endpoint_report(context)

    @visit('MULTI_CHANNEL_CAPABILITY_GET')
    def handle_capability_get(self, command: Command, context: Context):
        self.send_capability_report(context, endpoint=command.endpoint)

    @visit('MULTI_CHANNEL_END_POINT_FIND')
    def handle_endpoint_find(self, command: Command, context: Context):
        self.send_endpoint_find_report(context,
                                       generic=command.generic_device_class,
                                       specific=command.specific_device_class)

    @visit('MULTI_CHANNEL_CMD_ENCAP')
    def handle_encapsulated_command(self, command: Command, context: Context):
        def each_channel() -> Iterator[Channel]:
            if command.bit_address:
                for channel_id in each_bit(command.destination, start=1):
                    yield self.node.channels[channel_id]
            else:
                yield self.node.channels[command.destination]

        context = context.copy(endpoint=command.source_endpoint)
        for channel in each_channel():
            channel.handle_command(command.command, context)

    def send_endpoint_report(self, context: Context):
        self.send_command(context, 'MULTI_CHANNEL_END_POINT_REPORT',
                          dynamic=False,
                          identical=self.check_identical_channels(),
                          endpoints=len(self.node.channels) - 1)

    def send_capability_report(self, context: Context, endpoint: int):
        channel = self.node.channels[endpoint]

        self.send_command(context, 'MULTI_CHANNEL_CAPABILITY_REPORT',
                          dynamic=False,
                          endpoint=endpoint,
                          generic_device_class=channel.generic,
                          specific_device_class=channel.specific,
                          command_class_ids=[cc.class_id for cc in channel.command_classes.values()
                                             if cc.advertise_in_nif and cc.supported_non_securely and cc is not self])

    def send_endpoint_find_report(self, context: Context, generic: int, specific: int):
        self.send_command(context, 'MULTI_CHANNEL_END_POINT_FIND_REPORT',
                          reports_to_follow=0,
                          generic_device_class=generic,
                          specific_device_class=specific,
                          endpoints=[channel.endpoint for channel in self.find_channels(generic, specific)])

    def send_encapsulated_command(self, context: Context, source_endpoint: int, command: List[int]):
        self.send_command(context, 'MULTI_CHANNEL_CMD_ENCAP',
                          source_endpoint=source_endpoint,
                          bit_address=False,
                          destination=context.endpoint,
                          command=command)

    def find_channels(self, generic: int, specific: int) -> List[Channel]:
        return [channel for channel in self.node.channels
                if channel.generic == generic and channel.specific == specific]

    def check_identical_channels(self) -> bool:
        prototype = self.node.channels[1]

        def key(channel):
            return channel.generic == prototype.generic and \
                   channel.specific == prototype.specific and \
                   channel.command_classes == prototype.command_classes

        return all(key(channel) for channel in self.node.channels[2:])
