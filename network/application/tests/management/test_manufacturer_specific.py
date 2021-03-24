from ..fixture import *

from network.application.command_classes.command_class_factory import command_class_factory


@pytest.fixture(autouse=True)
def command_class(node):
    yield command_class_factory.create_command_class('COMMAND_CLASS_MANUFACTURER_SPECIFIC',
                                                     node,
                                                     manufacturer_id=1,
                                                     product_type_id=2,
                                                     product_id=3)


def test_manufacturer_specific_get(rx, tx):
    rx('MANUFACTURER_SPECIFIC_GET')
    tx('MANUFACTURER_SPECIFIC_REPORT', manufacturer_id=1, product_type_id=2, product_id=3)
