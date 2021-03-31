import os
from pathlib import Path
from tinydb import TinyDB


class BaseDatabaseProvider:
    def __init__(self, storage_path: str):
        project_root = Path(__file__).parts[:-3]

        self.db = TinyDB(os.path.join(*project_root, storage_path), create_dirs=True)
