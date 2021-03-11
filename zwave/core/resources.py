from tools import load_yaml


class Resources:
    def __init__(self):
        self.data = load_yaml("zwave/resources/config.yaml")

    def __getitem__(self, key):
        return self.data[key]
