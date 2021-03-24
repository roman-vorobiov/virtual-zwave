from ..fixture import *

from network.application.command_classes.command_class_factory import command_class_factory


@pytest.fixture(autouse=True)
def command_class(node):
    yield command_class_factory.create_command_class('COMMAND_CLASS_BASIC', node)


def test_basic_get(rx, tx):
    rx('BASIC_GET')
    tx('BASIC_REPORT', value=0xFE)


def test_basic_set(rx, tx, command_class):
    rx('BASIC_SET', value=123)
    assert command_class.value == 123

    rx('BASIC_GET')
    tx('BASIC_REPORT', value=123)
