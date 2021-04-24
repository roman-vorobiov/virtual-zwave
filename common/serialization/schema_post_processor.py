from .schema import Schema
from .utils import RangedFieldsResolver, MarkerResolver


class SchemaPostProcessor:
    def __init__(self):
        self.marker_resolver = MarkerResolver()
        self.ranged_fields_resolver = RangedFieldsResolver()

    def process(self, schema: Schema):
        self.marker_resolver.resolve_marker_fields(schema)
        self.ranged_fields_resolver.resolve_ranged_fields(schema)
