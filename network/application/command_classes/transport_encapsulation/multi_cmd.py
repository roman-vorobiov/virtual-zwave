from ..command_class import CommandClass, command_class

from network.protocol import Command

from tools import visit, make_object

from typing import List


@command_class('COMMAND_CLASS_MULTI_CMD', version=1)
class MultiCmd1(CommandClass):
    @visit('MULTI_CMD_ENCAP')
    def handle_encap(self, command: Command):
        with self.update_context(multi_cmd_response_queue=[]):
            for encap in command.commands:
                self.channel.handle_command(encap.command)
            commands = self.context.multi_cmd_response_queue

        self.send_encapsulated_command(commands)

    def send_encapsulated_command(self, commands: List[List[int]]):
        command = self.prepare_encapsulated_command(commands)
        self.send_command(command)

    def prepare_encapsulated_command(self, commands: List[List[int]]):
        return self.make_command('MULTI_CMD_ENCAP',
                                 commands=[make_object(command=command) for command in commands])
