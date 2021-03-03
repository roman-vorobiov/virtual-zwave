from zwave.core import ZwaveDevice, Core

import signal
from threading import Thread


def listener(device: ZwaveDevice, handler: Core):
    for packet in device.poll():
        handler.process_packet(packet)


class Daemon:
    def __init__(self, link: str):
        self.device = ZwaveDevice(link)
        self.handler = Core(self.device)
        self.polling_job = Thread(target=listener, args=(self.device, self.handler))

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
