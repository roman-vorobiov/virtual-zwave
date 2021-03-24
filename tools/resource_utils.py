import yaml
import os
from pathlib import Path
from typing import Dict


PROJECT_ROOT = Path(__file__).parent.parent.absolute()


def load_yaml(source: str) -> Dict:
    with open(os.path.join(PROJECT_ROOT, source)) as resource:
        return yaml.safe_load(resource)


class Resources:
    def __init__(self, *paths: str):
        self.data = {}

        for path in paths:
            self.data.update(load_yaml(path))

    def __getitem__(self, key):
        return self.data[key]
