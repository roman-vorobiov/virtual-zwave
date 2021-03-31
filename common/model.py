class Model:
    def __init__(self):
        self.id = None
        self.repository = None

    def __eq__(self, other: 'Model') -> bool:
        return self.id is not None and self.id == other.id

    def register(self, id, repository):
        self.id = id
        self.repository = repository

    def save(self):
        if self.repository:
            self.repository.update(self)
