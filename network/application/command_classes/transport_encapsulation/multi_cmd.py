from ..command_class import CommandClass, command_class

from network.protocol import Command

from tools import visit, Object, make_object

from typing import List


@command_class('COMMAND_CLASS_MULTI_CMD', version=1)
class MultiCmd1(CommandClass):
    @visit('MULTI_CMD_ENCAP')
    def handle_encap(self, command: Command):
        commands = self.process_commands(command.commands)
        self.send_encapsulated_command(commands)

    def send_encapsulated_command(self, commands: List[List[int]]):
        self.send_command('MULTI_CMD_ENCAP',
                          commands=[make_object(command=command) for command in commands])

    def process_commands(self, commands: List[Object]) -> List[List[int]]:
        with self.update_context(multi_cmd_response_queue=[]):
            for encap in commands:
                self.channel.handle_command(encap.command)

            return self.context.multi_cmd_response_queue
