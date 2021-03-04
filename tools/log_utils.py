from termcolor import cprint
from datetime import datetime
from enum import IntFlag
from typing import List


def timestamp_prefix() -> str:
    return f"[{datetime.now().strftime('%H:%M:%S.%f')}]"


def print_with_timestamp(message: str, color=None):
    cprint(f"{timestamp_prefix()} {message}", color)


def log_debug(message: str):
    print_with_timestamp(message, 'blue')


def log_info(message: str):
    print_with_timestamp(message)


def log_warning(message: str):
    print_with_timestamp(message, 'yellow')


def log_error(message: str):
    print_with_timestamp(message, 'red')


def dump_hex(data: List[int]):
    return "[{}]".format(" ".join("{:02x}".format(byte) for byte in data))


def flags_to_names_list(enum: IntFlag) -> List[str]:
    return [option.name for option in type(enum) if enum & option]
