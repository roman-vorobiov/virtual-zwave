from ..fixture import *

from network.application.command_classes.application.basic import Basic


@pytest.fixture(autouse=True)
def command_class(node):
    yield node.add_command_class(Basic)


def test_basic_get(rx, tx):
    rx('BASIC_GET')
    tx('BASIC_REPORT', value=0xFE)


def test_basic_set(rx, tx, command_class):
    rx('BASIC_SET', value=123)
    assert command_class.value == 123

    rx('BASIC_GET')
    tx('BASIC_REPORT', value=123)