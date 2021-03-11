from .resources import Resources

from zwave.protocol.commands.version import LibraryType


class Library:
    def __init__(self, resources: Resources):
        self.version = resources['VERSION']
        self.library_type = LibraryType.CONTROLLER_STATIC
