import unittest.mock
import asyncio


class EventMock(unittest.mock.Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = asyncio.Event()

    def _mock_call(self, *args, **kwargs):
        super()._mock_call(*args, **kwargs)
        self.event.set()

    def reset_mock(self, *args, **kwargs):
        super().reset_mock(*args, **kwargs)
        self.event.clear()

    async def wait_until_called(self, timeout=1):
        await asyncio.wait_for(self.event.wait(), timeout)


class SequencedMock(unittest.mock.Mock):
    def assert_called_first_with(self, *args, **kwargs):
        assert self.called

        actual = self.mock_calls[0]
        expected = unittest.mock.call(*args, **kwargs)

        assert actual == expected

    def pop_first_call(self):
        self.mock_calls.pop(0)
        self.call_args_list.pop(0)
        self.call_count -= 1
        if self.call_count == 0:
            self.called = False


class Mock(SequencedMock, EventMock):
    def pop_first_call(self):
        super().pop_first_call()
        if not self.called:
            self.event.clear()
