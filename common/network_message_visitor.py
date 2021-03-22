from tools import Visitor, log_info


class NetworkMessageVisitor(Visitor):
    def visit(self, message: dict, *args, **kwargs):
        log_info(f"{message}")
        return self.visit_as(message['message'], message['messageType'], *args, **kwargs)
