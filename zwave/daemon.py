from zwave.core import ZwaveDevice, Core

import signal
import asyncio


async def listener(device: ZwaveDevice, handler: Core):
    async for packet in device.poll():
        handler.process_packet(packet)


class Daemon:
    def __init__(self, link: str):
        self.device = ZwaveDevice(link)
        self.handler = Core(self.device)

    def run(self):
        self.device.initialize()

        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, lambda *_: self.stop())

        asyncio.run(listener(self.device, self.handler))

    def stop(self):
        self.device.finalize()
