from typing import Iterator, Optional


class LookaheadIterator:
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self.buffer:
            return self.buffer.pop()
        else:
            return next(self.iterator)

    def has_next(self):
        if self.buffer:
            return True

        try:
            self.buffer = [next(self.iterator)]
        except StopIteration:
            return False
        else:
            return True


def until_exhausted(it: Optional[Iterator], stop: Optional[int] = None) -> Iterator[Iterator]:
    if it is None:
        return

    if stop is not None:
        for _ in range(stop):
            yield it
    else:
        i = LookaheadIterator(it)
        while i.has_next():
            yield i


def empty_async_generator(fn):
    async def inner(*args, **kwargs):
        await fn(*args, **kwargs)

        # No "yield from []" in async functions :(
        return
        yield

    return inner
