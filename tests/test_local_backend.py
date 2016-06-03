# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shutil
import tempfile

from os.path import join, exists

from . import TestCase
from .test_backend_mixin import BackendTestMixin

from flask_fs.backends.local import LocalBackend
from flask_fs.storage import Config


class LocalBackendTest(BackendTestMixin, TestCase):
    def setUp(self):
        super(LocalBackendTest, self).setUp()
        self.test_dir = tempfile.mkdtemp()
        self.config = Config({
            'root': self.test_dir,
        })
        self.backend = LocalBackend('test', self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def filename(self, filename):
        return join(self.test_dir, filename)

    def put_file(self, filename, content):
        with open(self.filename(filename), 'wb') as f:
            f.write(self.b(content))

    def get_file(self, filename):
        with open(self.filename(filename), 'rb') as f:
            return f.read()

    def file_exists(self, filename):
        return exists(self.filename('file.test'))

    def test_root(self):
        self.assertEqual(self.backend.root, self.test_dir)

    def test_default_root(self):
        self.app.config['FS_ROOT'] = self.test_dir
        root = self.filename('default')
        backend = LocalBackend('default', Config({}))
        with self.app.app_context():
            self.assertEqual(backend.root, root)
