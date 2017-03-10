# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from . import BaseBackend

log = logging.getLogger(__name__)


class MockBackend(BaseBackend):
    '''
    A backend with only purpose of being mocked
    '''
    pass
