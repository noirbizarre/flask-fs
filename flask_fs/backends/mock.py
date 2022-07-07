import logging

from . import BaseBackend

log = logging.getLogger(__name__)


class MockBackend(BaseBackend):
    '''
    A backend with only purpose of being mocked
    '''
    pass
