import pampy
from typing import Optional, List


def unroll(obj):
    return pampy.match(obj,
                       dict, unroll_dict,
                       list, unroll_list,
                       pampy._, unroll_object)


def unroll_dict(state: dict):
    for key, value in state.items():
        state[key] = unroll(value)

    return state


def unroll_list(state: list):
    for idx, item in enumerate(state):
        state[idx] = unroll(item)

    return state


def unroll_object(obj):
    if (state_getter := getattr(obj, '__getstate__', None)) is not None:
        return state_getter()
    else:
        return obj


def serializable(excluded_fields: Optional[List] = None):
    def __getstate__(self) -> dict:
        state = {key: value for key, value in self.__dict__.items() if key not in (excluded_fields or {})}
        unroll(state)
        return state

    def inner(cls):
        setattr(cls, '__getstate__', __getstate__)
        setattr(cls, 'to_dict', __getstate__)
        return cls

    return inner
