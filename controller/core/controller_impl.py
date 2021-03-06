from .controller import Controller

from controller.protocol.packet_builder import PacketBuilder, Bytes

from tools import SerialPort, log_warning, log_debug, dump_hex

from typing import AsyncIterator


class ControllerImpl(Controller):
    def __init__(self, link: str):
        self.port = SerialPort(
            link=link,
            options="b115200,parenb=0,parodd=0,cs8,cstopb=0,crtscts=0,echo=0"
        )
        self.packet_builder = PacketBuilder()
        self.running = False

    def initialize(self):
        self.port.open()
        self.running = True

    def finalize(self):
        self.running = False
        self.port.close()

    async def poll(self) -> AsyncIterator[Bytes]:
        while True:
            if (data := await self.port.read_byte()) is not None:
                byte = int.from_bytes(data, byteorder='big')
                if (packet := self.packet_builder.process(byte)) is not None:
                    log_debug(f"RX: {dump_hex(packet)}")
                    yield packet
            elif self.running:
                log_warning("Pipe broken")
                self.packet_builder.reset()
                self.port.open()
            else:
                break

    def send_data(self, data: Bytes):
        log_debug(f"TX: {dump_hex(data)}")
        self.port.write_bytes(bytes(data))
