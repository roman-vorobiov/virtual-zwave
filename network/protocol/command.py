from tools import Object, Visitor, dump_hex, log_info

import json


Command = Object


def make_command(class_id: int, name: str, class_version=1, /, **kwargs) -> Command:
    return Command(data=kwargs, meta={'name': name, 'class_id': class_id, 'class_version': class_version})


class CommandVisitor(Visitor):
    def visit(self, command: Command, *args, **kwargs):
        return self.visit_as(command, command.get_meta('name'), *args, **kwargs)


def log_command(sender_id: int, sender_endpoint: int, receiver_id: int, receiver_endpoint: int, command: Command):
    command_json = command.to_json()
    for key, value in command_json.items():
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], int):
                command_json[key] = dump_hex(value)

    prefix = f"{sender_id}:{sender_endpoint} -> {receiver_id}:{receiver_endpoint}"
    log_info(f"{prefix} {command.get_meta('name')} {json.dumps(command_json)}")
