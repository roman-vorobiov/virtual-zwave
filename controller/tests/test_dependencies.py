from controller.core import Core

from tools import Mock


def test_dependencies():
    Core(Mock(), Mock())
