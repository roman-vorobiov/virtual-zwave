from zwave.protocol.commands.version import LibraryType

from tools import Resources


class Library:
    def __init__(self, config: Resources):
        self.version = config['VERSION']
        self.library_type = LibraryType.CONTROLLER_STATIC
