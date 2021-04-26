from tools import Serializable


class Model(Serializable):
    def __init__(self):
        self.id = None
        self.repository = None

    def __getstate__(self):
        return {
            'id': self.id
        }

    def __eq__(self, other: 'Model') -> bool:
        return self.id is not None and self.id == other.id

    def register(self, id, repository):
        self.id = id
        self.repository = repository

    def save(self):
        if self.repository:
            self.repository.update(self)
