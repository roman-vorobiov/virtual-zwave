from websockets import WebSocketCommonProtocol
from asyncio import Queue
from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator


class NetworkConnection(ABC):
    def __init__(self):
        self.queue: Optional[Queue] = None
        self.websocket: Optional[WebSocketCommonProtocol] = None

    def initialize(self):
        self.queue = Queue()

    @property
    def open(self) -> bool:
        return self.websocket is not None and self.websocket.open

    async def poll(self) -> AsyncIterator[str]:
        while (message := await self.queue.get()) is not None:
            yield message

    async def close(self):
        await self.queue.put(None)

    async def start_polling(self):
        async for message in self.websocket:
            await self.queue.put(message)

    @abstractmethod
    async def send_data(self, data: str):
        pass
