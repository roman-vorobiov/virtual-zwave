class VisitorMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.__visit_dispatcher__ = dict(cls.get_visit_methods())

    def get_visit_methods(cls):
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            if hasattr(attribute, '__visited_classes__'):
                for visited_class in attribute.__visited_classes__:
                    yield visited_class, attribute


class Visitor(metaclass=VisitorMeta):
    def visit(self, obj, *args, **kwargs):
        return self.visit_as(obj, obj.__class__, *args, **kwargs)

    def visit_as(self, obj, identity, *args, **kwargs):
        visit_method = self.__visit_dispatcher__.get(identity, self.__class__.visit_default)
        return visit_method(self, obj, *args, **kwargs)

    def visit_default(self, obj, *args, **kwargs):
        raise KeyError(obj.__class__)


def visit(*classes):
    def wrapper(fn):
        fn.__visited_classes__ = classes
        return fn

    return wrapper
