from ...utils import SecurityUtils

from tools import Mock

import pytest


@pytest.fixture(scope='class')
def security_utils():
    yield SecurityUtils()


@pytest.fixture(scope='session')
def state_observer():
    yield Mock()
