from tools import Visitor


class RemoteMessageVisitor(Visitor):
    def visit(self, message: dict, *args, **kwargs):
        return self.visit_as(message['message'], message['messageType'], *args, **kwargs)

    def visit_default(self, message: dict, message_type: str):
        raise KeyError(message_type)
