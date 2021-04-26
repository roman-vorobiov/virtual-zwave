from .meta import create_marker


VisitorMeta, visit = create_marker('__visit_dispatcher__', '__visited_classes__')


class Visitor(metaclass=VisitorMeta):
    def visit(self, obj, *args, **kwargs):
        return self.visit_as(obj, obj.__class__, *args, **kwargs)

    def visit_as(self, obj, identity, *args, **kwargs):
        if (visit_method := self.__visit_dispatcher__.get(identity)) is not None:
            return visit_method(self, obj, *args, **kwargs)
        else:
            return self.visit_default(obj, identity)

    def visit_default(self, obj, identity):
        raise KeyError(identity)
