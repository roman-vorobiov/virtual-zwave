from tools import Visitor


class RemoteMessageVisitor(Visitor):
    def visit(self, message: dict, *args, **kwargs):
        return self.visit_as(message['message'], message['messageType'], *args, **kwargs)
