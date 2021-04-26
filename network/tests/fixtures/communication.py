import pytest


@pytest.fixture
def tx_client(client):
    def inner(message_type: str, message: dict):
        client.send_message.assert_called_first_with(message_type, message)

    return inner
