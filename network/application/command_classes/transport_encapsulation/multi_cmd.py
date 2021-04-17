from ..command_class import CommandClass, command_class
from ...request_context import Context

from network.protocol import Command

from tools import visit, make_object

from typing import List


@command_class('COMMAND_CLASS_MULTI_CMD', version=1)
class MultiCmd1(CommandClass):
    @visit('MULTI_CMD_ENCAP')
    def handle_encap(self, command: Command, context: Context):
        temp_context = context.copy(multi_cmd_response_queue=[])
        for encap in command.commands:
            self.channel.handle_command(encap.command, temp_context)

        self.send_encapsulated_command(context, temp_context.multi_cmd_response_queue)

    def send_encapsulated_command(self, context: Context, commands: List[List[int]]):
        self.send_command(context, 'MULTI_CMD_ENCAP',
                          commands=[make_object(command=command) for command in commands])
