from .log_utils import log_info

import os
import signal
import asyncio
from subprocess import Popen, PIPE
from typing import Optional


class SerialPort:
    def __init__(self, link: str, options: str):
        self.link = link
        self.options = options
        self.proc: Optional[Popen] = None

    def open(self):
        address = f"PTY,link={self.link},{self.options},rawer,wait-slave"
        self.proc = Popen(["socat", address, "-"], stdin=PIPE, stdout=PIPE)
        log_info(f"Serial device created at {self.link}")

    def close(self):
        if self.is_open:
            os.kill(self.proc.pid, signal.SIGTERM)
            log_info(f"Serial device removed")
        self.proc = None

    @property
    def is_open(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    async def read_byte(self) -> Optional[bytes]:
        data = await asyncio.get_event_loop().run_in_executor(None, self.proc.stdout.read, 1)
        if self.is_open:
            return data

    def write_bytes(self, data: bytes):
        self.proc.stdin.write(data)
        self.proc.stdin.flush()
