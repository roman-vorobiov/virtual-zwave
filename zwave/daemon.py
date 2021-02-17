from .chip import ZwaveChip

from tools import dump_hex

import signal
from threading import Thread
from typing import List


def handler(packet: List[int]):
    print(dump_hex(packet))


def listener(device: ZwaveChip):
    for packet in device.poll():
        handler(packet)


class Daemon:
    def __init__(self, link: str):
        self.device = ZwaveChip(link)
        self.polling_job = Thread(target=listener, args=(self.device,))

    def run(self):
        self.device.initialize()
        self.polling_job.start()

        def teardown(sig, frame):
            self.stop()
            exit(0)

        signal.signal(signal.SIGINT, teardown)
        signal.signal(signal.SIGTERM, teardown)
        signal.pause()

    def stop(self):
        self.device.finalize()

        if self.polling_job.is_alive():
            self.polling_job.join()
