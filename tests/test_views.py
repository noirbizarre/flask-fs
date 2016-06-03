# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import shutil
import tempfile

from flask import url_for

from . import TestCase

import flask_fs as fs


class MockBackend(fs.BaseBackend):
    pass


MOCK_BACKEND = '.'.join((__name__, MockBackend.__name__))


def mock_backend(func):
    return mock.patch(MOCK_BACKEND)(func)


class ViewsTestCase(TestCase):
    def setUp(self):
        super(ViewsTestCase, self).setUp()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def configure(self, *storages, **configs):
        self.app.config['FS_BACKEND'] = configs.pop('FS_BACKEND', MOCK_BACKEND)
        super(ViewsTestCase, self).configure(*storages, **configs)

    def test_url(self):
        storage = fs.Storage('test')

        self.configure(storage)

        with self.app.test_request_context('/'):
            expected_url = url_for('fs.get_file', fs=storage.name, filename='test.txt')
            self.assertEqual(storage.url('test.txt'), expected_url)

    @mock_backend
    def test_get_file(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.serve.return_value = 'content'.encode('utf-8')

        self.configure(storage)

        with self.app.test_request_context():
            file_url = url_for('fs.get_file', fs='test', filename='test.txt')

        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'content'.encode('utf-8'))

    @mock_backend
    def test_get_file_not_found(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.exists.return_value = False

        self.configure(storage)

        with self.app.test_request_context('/'):
            file_url = url_for('fs.get_file', fs='test', filename='test.txt')

        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 404)

    def test_get_file_no_storage(self):
        self.configure()

        with self.app.test_request_context('/'):
            file_url = url_for('fs.get_file', fs='fake', filename='test.txt')

        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 404)
