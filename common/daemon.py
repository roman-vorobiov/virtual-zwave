import asyncio
import signal
from abc import ABC, abstractmethod


class Daemon(ABC):
    def run(self):
        for sig in [signal.SIGINT, signal.SIGTERM]:
            asyncio.get_event_loop().add_signal_handler(sig, self.stop)

        asyncio.get_event_loop().run_until_complete(self.start())
        asyncio.get_event_loop().close()

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
