def create_marker(collection_name: str, marker_name: str):
    def get_marked_methods(cls):
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            for method in getattr(attribute, marker_name, []):
                yield method, attribute

    class Meta(type):
        def __init__(cls, *args, **kwargs):
            super().__init__(*args, **kwargs)
            cls.collect_markers()

        def collect_markers(cls):
            setattr(cls, collection_name, dict(get_marked_methods(cls)))

    def marker(*args):
        def inner(fn):
            setattr(fn, marker_name, args)
            return fn

        return inner

    return Meta, marker
