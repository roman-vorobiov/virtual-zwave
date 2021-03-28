from tools import Object, Visitor


Command = Object


def make_command(class_id: int, name: str, **kwargs) -> Command:
    return Command(data=kwargs, meta={'name': name, 'class_id': class_id})


class CommandVisitor(Visitor):
    def visit(self, command: Command, *args, **kwargs):
        return self.visit_as(command, command.get_meta('name'), *args, **kwargs)
