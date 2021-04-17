from ..fixtures import *

from network.application.command_classes.management import ManufacturerSpecific1


class TestManufacturerSpecific1:
    @pytest.fixture(scope='class', autouse=True)
    def command_class(self, channel):
        yield channel.add_command_class(ManufacturerSpecific1, manufacturer_id=1, product_type_id=2, product_id=3)

    def test_manufacturer_specific_get(self, rx, tx):
        rx('MANUFACTURER_SPECIFIC_GET')
        tx('MANUFACTURER_SPECIFIC_REPORT', manufacturer_id=1, product_type_id=2, product_id=3)
