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

        actual = self.pop_first_call()
        expected = unittest.mock.call(*args, **kwargs)

        assert actual == expected

    def pop_first_call(self) -> unittest.mock.call:
        call = self.mock_calls.pop(0)
        self.call_args_list.pop(0)
        self.call_count -= 1
        if self.call_count == 0:
            self.called = False

        return call


class Mock(SequencedMock, EventMock):
    def pop_first_call(self) -> unittest.mock.call:
        call = super().pop_first_call()

        if not self.called:
            self.event.clear()

        return call

    def assert_methods_not_called(self):
        for method in self._mock_children.values():
            method.assert_not_called()
