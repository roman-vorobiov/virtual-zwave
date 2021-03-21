from zwave.protocol import Packet


def make_command(class_id: int, command_name: str, **kwargs) -> Packet:
    command = Packet(command_name, **kwargs)
    command.class_id = class_id
    return command
