import pampy


def unroll(obj):
    return pampy.match(obj,
                       dict, lambda state: {key: unroll(value) for key, value in state.items()},
                       list, lambda state: [unroll(item) for item in state],
                       Serializable, lambda state: state.to_dict(),
                       default=obj)


class Serializable:
    def __getstate__(self):
        return self.__dict__

    def to_dict(self):
        return unroll(self.__getstate__())
