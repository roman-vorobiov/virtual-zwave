from .device import Device

from zwave.protocol.packet_builder import PacketBuilder, Bytes

from tools.serial_port import SerialPort

from typing import Iterator


class ZwaveDevice(Device):
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

    def poll(self) -> Iterator[Bytes]:
        while True:
            data = self.port.read_byte()
            if data is not None:
                byte = int.from_bytes(data, byteorder='big')
                yield from self.packet_builder.process(byte)
            elif self.running:
                print("Pipe broken")
                self.packet_builder.reset()
                self.port.open()
            else:
                break

    def send_data(self, data: Bytes):
        self.port.write_bytes(bytes(data))
