from .meta import create_marker


VisitorMeta, visit = create_marker('__visit_dispatcher__', '__visited_classes__')


class Visitor(metaclass=VisitorMeta):
    def visit(self, obj, *args, **kwargs):
        return self.visit_as(obj, obj.__class__, *args, **kwargs)

    def visit_as(self, obj, identity, *args, **kwargs):
        visit_method = self.__visit_dispatcher__.get(identity, self.__class__.visit_default)
        return visit_method(self, obj, *args, **kwargs)

    def visit_default(self, obj, *args, **kwargs):
        raise KeyError(obj.__class__)
