from tools import Object, Visitor


Command = Object


def make_command(_class_id: int, _name: str, _class_version=1, **kwargs) -> Command:
    return Command(data=kwargs, meta={'name': _name, 'class_id': _class_id, 'class_version': _class_version})


class CommandVisitor(Visitor):
    def visit(self, command: Command, *args, **kwargs):
        return self.visit_as(command, command.get_meta('name'), *args, **kwargs)
