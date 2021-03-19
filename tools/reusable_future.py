from asyncio import Future


class ReusableFuture:
    def __init__(self):
        self.impl = Future()
        self.waiting = False

    def __await__(self):
        self.waiting = True
        result = yield from self.impl
        self.waiting = False
        self.impl = Future()
        return result

    def cancel(self):
        if self.waiting:
            self.impl.cancel()

    def set_result(self, value):
        if self.waiting:
            self.impl.set_result(value)
