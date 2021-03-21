from tools import Visitor


class NetworkMessageVisitor(Visitor):
    def visit(self, message: dict, *args, **kwargs):
        print(f"RX: {message}")
        return self.visit_as(message['message'], message['messageType'], *args, **kwargs)
