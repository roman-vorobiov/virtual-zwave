import pampy
from typing import Optional, List


def unroll(obj):
    return pampy.match(obj,
                       dict, unroll_dict,
                       list, unroll_list,
                       pampy._, unroll_object)


def unroll_dict(state: dict):
    return {key: unroll(value) for key, value in state.items()}


def unroll_list(state: list):
    return [unroll(item) for item in state]


def unroll_object(obj):
    if (state_getter := getattr(obj, '__getstate__', None)) is not None:
        return state_getter()
    else:
        return obj


def serializable(cls=None, /, *, excluded_fields: Optional[List[str]] = None, class_fields: Optional[List[str]] = None):
    def __getstate__(self) -> dict:
        state = {key: getattr(self.__class__, key) for key in class_fields or []}

        state.update({key: value for key, value in self.__dict__.items() if key not in (excluded_fields or [])})

        return unroll(state)

    def inner(cls):
        setattr(cls, '__getstate__', __getstate__)
        setattr(cls, 'to_dict', __getstate__)
        return cls

    if cls is None:
        return inner
    else:
        return inner(cls)
