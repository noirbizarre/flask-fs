# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import os
import six
import mock

from flask import Flask
from werkzeug.datastructures import FileStorage

import flask_fs as fs

import pytest

BIN_FILE = os.path.join(os.path.dirname(__file__), 'flask.png')


class TestConfig:
    TESTING = True
    MONGODB_DB = 'flask-fs-test'
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017


class TestFlask(Flask):
    def configure(self, *storages, **configs):
        import flask_fs as fs
        for key, value in configs.items():
            self.config[key] = value
        fs.init_app(self, *storages)


@pytest.fixture
def app():
    app = TestFlask('flaskfs-tests')
    app.config.from_object(TestConfig)
    yield app


class Utils(object):
    def __init__(self, faker):
        self.faker = faker

    def filestorage(self, filename, content):
        return FileStorage(self.file(content), filename)

    def file(self, content):
        if isinstance(content, six.binary_type):
            return io.BytesIO(content)
        elif isinstance(content, six.string_types):
            return io.BytesIO(content.encode('utf-8'))
        else:
            return content

    def b(self, content):
        if isinstance(content, six.string_types):
            content = six.b(content)
        return content

    def text(self):
        return six.text_type(self.faker.sentence())

    def binary(self):
        return six.binary_type(self.faker.binary())


@pytest.fixture
def utils(faker):
    return Utils(faker)


class MockBackend(fs.BaseBackend):
    pass


MOCK_BACKEND = '.'.join((__name__, MockBackend.__name__))


@pytest.fixture
def mock_backend(app):
    app.config['FS_BACKEND'] = MOCK_BACKEND
    patcher = mock.patch(MOCK_BACKEND)
    yield patcher.start()
