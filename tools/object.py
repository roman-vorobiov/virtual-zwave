import humps
from typing import Any, Optional


class Object:
    def __init__(self, data: dict, meta: Optional[dict] = None):
        super().__setattr__('_data', data)
        super().__setattr__('_meta', meta or {})

    @classmethod
    def from_json(cls, json: dict) -> 'Object':
        return Object(humps.decamelize(json), meta={})

    def to_json(self) -> dict:
        return humps.camelize(self._data)

    def __repr__(self):
        if self._meta == {}:
            return self._data.__repr__()
        else:
            return f"{self._meta.__repr__()} {self._data.__repr__()}"

    def __eq__(self, other: 'Object'):
        return self._meta == other._meta and self._data == other._data

    def __getattr__(self, field_name: str) -> Any:
        return self._data.get(field_name)

    def __setattr__(self, field_name: str, value: Any):
        self._data[field_name] = value

    def get_data(self) -> dict:
        return self._data

    def get_meta(self, key: str) -> Any:
        return self._meta.get(key)

    def set_meta(self, key: str, value: Any):
        self._meta[key] = value


def make_object(**kwargs) -> Object:
    return Object(data=kwargs, meta={})
