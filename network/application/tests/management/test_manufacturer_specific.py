from ..fixture import *

from network.application.command_classes.management import ManufacturerSpecific1


@pytest.fixture(autouse=True)
def command_class(channel):
    yield ManufacturerSpecific1(channel, manufacturer_id=1, product_type_id=2, product_id=3)


def test_manufacturer_specific_get(rx, tx):
    rx('MANUFACTURER_SPECIFIC_GET')
    tx('MANUFACTURER_SPECIFIC_REPORT', manufacturer_id=1, product_type_id=2, product_id=3)
