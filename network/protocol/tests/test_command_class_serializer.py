from .fixtures import APPLICATION, MANAGEMENT, TRANSPORT_ENCAPSULATION
from network.tests.fixtures.components import command_class_serializer

import pytest


@pytest.mark.parametrize("data,expected", [*APPLICATION, *MANAGEMENT, *TRANSPORT_ENCAPSULATION])
def test_serialization(command_class_serializer, data, expected):
    command = command_class_serializer.from_bytes(data, expected.get_meta('class_version'))
    assert command == expected
    assert command_class_serializer.to_bytes(command) == data
