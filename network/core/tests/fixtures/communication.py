import pytest


@pytest.fixture
def tx_controller(controller):
    def inner(message_type: str, message: dict):
        assert controller.free_buffer() == [{
            'messageType': message_type,
            'message': message
        }]

    yield inner


@pytest.fixture(autouse=True)
def check_communication(controller, client):
    yield
    assert controller.free_buffer() == []
    client.send_message.assert_not_called()
