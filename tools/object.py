from typing import Any


class Object:
    def __init__(self, **kwargs):
        self.fields = kwargs

    def __eq__(self, other: 'Object'):
        return self.fields == other.fields

    def __getattr__(self, field_name: str) -> Any:
        return self.fields.get(field_name)

    def __getitem__(self, field_name: str) -> Any:
        return self.fields.get(field_name)

    def __setitem__(self, field_name: str, value: Any):
        self.fields[field_name] = value
