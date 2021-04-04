from .components import *
from .seed import *

from network.protocol import make_command

import pytest


@pytest.fixture
def tx(channel, command_class):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, **kwargs)
        channel.send_command.assert_called_first_with(1, command)
        channel.send_command.pop_first_call()

    yield inner


@pytest.fixture
def rx(command_class):
    def inner(name: str, **kwargs):
        command = make_command(command_class.class_id, name, **kwargs)
        command_class.handle_command(1, command)

    yield inner


@pytest.fixture(autouse=True)
def check_communication(channel):
    yield
    channel.send_command.assert_not_called()
