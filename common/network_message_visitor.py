from tools import Visitor, log_info

import json


class NetworkMessageVisitor(Visitor):
    def visit(self, message: dict, *args, **kwargs):
        log_info(json.dumps(message, indent=4))
        return self.visit_as(message['message'], message['messageType'], *args, **kwargs)
