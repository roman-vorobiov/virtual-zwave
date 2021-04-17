from network.tests.fixtures.components import *

from ...utils import SecurityUtils

import pytest


@pytest.fixture(scope='class')
def security_utils():
    yield SecurityUtils()
