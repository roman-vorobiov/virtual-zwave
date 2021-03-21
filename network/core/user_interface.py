import asyncio
from asyncio import CancelledError
from aioconsole import ainput

from typing import AsyncIterator


class UserInterface:
    def __init__(self):
        self.task = None

    def stop(self):
        self.task.cancel()

    async def poll(self) -> AsyncIterator[str]:
        while True:
            try:
                self.task = asyncio.create_task(ainput())
                yield await self.task
            except CancelledError:
                self.stop()
                break
