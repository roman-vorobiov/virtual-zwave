from dataclasses import dataclass
from typing import List, Optional, TypeVar, Generic


T = TypeVar('T')


class RangeIterator(Generic[T]):
    @dataclass
    class State:
        idx: int

    def __init__(self, data: List[T], stop=None, state: Optional[State] = None):
        self.data = data
        self.stop = stop or len(data)
        self.state = state or RangeIterator.State(idx=0)

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if self.exhausted:
            raise StopIteration()

        value = self.data[self.state.idx]
        self.state.idx += 1
        return value

    def current(self) -> T:
        if self.exhausted:
            raise IndexError()

        return self.data[self.state.idx]

    @property
    def exhausted(self) -> bool:
        return self.state.idx >= self.stop

    def slice(self, stop: Optional[int]) -> 'RangeIterator[T]':
        if stop is None:
            stop = self.stop
        elif stop >= 0:
            stop = min(self.state.idx + stop, self.stop)
        else:
            stop = max(self.stop + stop, self.state.idx)

        return RangeIterator(self.data, stop, self.state)


def empty_async_generator(fn):
    async def inner(*args, **kwargs):
        await fn(*args, **kwargs)

        # No "yield from []" in async functions :(
        return
        yield

    return inner
