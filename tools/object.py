import humps
from typing import Any


class Object:
    def __init__(self, **kwargs):
        self.fields = kwargs

    @classmethod
    def from_json(cls, json: dict) -> 'Object':
        return Object(**humps.decamelize(json))

    def to_json(self) -> dict:
        return humps.camelize(self.fields)

    def __repr__(self):
        return self.fields.__repr__()

    def __eq__(self, other: 'Object'):
        return self.fields == other.fields

    def __getattr__(self, field_name: str) -> Any:
        return self.fields.get(field_name)

    def __getitem__(self, field_name: str) -> Any:
        return self.fields.get(field_name)

    def __setitem__(self, field_name: str, value: Any):
        self.fields[field_name] = value
