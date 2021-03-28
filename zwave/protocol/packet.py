from tools import Object, Visitor


Packet = Object


def make_packet(name: str, **kwargs) -> Packet:
    return Packet(data=kwargs, meta={'name': name})


class PacketVisitor(Visitor):
    def visit(self, packet: Packet, *args, **kwargs):
        return self.visit_as(packet, packet.get_meta('name'), *args, **kwargs)
