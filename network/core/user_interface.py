import asyncio
from asyncio import CancelledError
from aioconsole import ainput


class UserInterface:
    def __init__(self):
        self.task = None

    def stop(self):
        self.task.cancel()

    async def poll(self):
        while True:
            try:
                self.task = asyncio.create_task(ainput())
                yield await self.task
            except CancelledError:
                self.stop()
                break
