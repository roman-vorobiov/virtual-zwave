from asyncio import Future


class ReusableFuture:
    def __init__(self):
        self.impl = Future()
        self.waiting = False

    def __await__(self):
        self.waiting = True

        try:
            result = yield from self.impl
            return result
        finally:
            self.waiting = False
            self.impl = Future()

    def cancel(self):
        if self.waiting:
            self.impl.cancel()

    def set_result(self, value):
        if self.waiting:
            self.impl.set_result(value)
