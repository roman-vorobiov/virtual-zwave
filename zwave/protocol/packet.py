from tools import Object, Visitor


class Packet(Object):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name


class PacketVisitor(Visitor):
    def visit(self, packet: Packet, *args, **kwargs):
        return self.visit_as(packet, packet.name, *args, **kwargs)
