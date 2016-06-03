# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

from flask import url_for

from flask_fs import Storage, DEFAULTS
from flask_fs.backends.local import LocalBackend

from . import TestCase


class TestConfiguration(TestCase):
    def test_default_configuration(self):
        self.configure()
        self.assertFalse(self.app.config['FS_SERVE'])
        self.assertEqual(self.app.config['FS_ROOT'], join(self.app.instance_path, 'fs'))
        self.assertIsNone(self.app.config['FS_PREFIX'])
        self.assertIsNone(self.app.config['FS_URL'])

    def test_default_debug_configuration(self):
        self.configure(DEBUG=True)
        self.assertTrue(self.app.config['FS_SERVE'])
        self.assertEqual(self.app.config['FS_ROOT'], join(self.app.instance_path, 'fs'))
        self.assertIsNone(self.app.config['FS_PREFIX'])
        self.assertIsNone(self.app.config['FS_URL'])

    def test_not_configured(self):
        files = Storage('files')
        self.assertIsNone(files.backend)
        self.assertEqual(files.config, {})

    def test_default_f(self):
        files = Storage('files')
        self.configure(files)

        self.assertEqual(files.name, 'files')
        self.assertEqual(files.extensions, DEFAULTS)
        self.assertIsInstance(files.backend, LocalBackend)
        with self.app.test_request_context():
            self.assertEqual(files.base_url, url_for('fs.get_file', fs='files', filename='', _external=True))

        self.assertIn('files', self.app.extensions['fs'])
        self.assertEqual(self.app.extensions['fs']['files'], files)

    def test_custom_prefix(self):
        files = Storage('files')
        self.configure(files, FS_PREFIX='/test')

        self.assertEqual(files.name, 'files')
        self.assertEqual(files.extensions, DEFAULTS)
        self.assertIsInstance(files.backend, LocalBackend)
        with self.app.test_request_context():
            self.assertEqual(files.base_url, url_for('fs.get_file', fs='files', filename='', _external=True))
            self.assertEqual(files.base_url, 'http://localhost/test/files/')

    def test_custom_url(self):
        files = Storage('files')
        self.configure(files, FS_URL='http://somewhere.net/test/')
        with self.app.test_request_context():
            self.assertEqual(files.base_url, 'http://somewhere.net/test/files/')

    def test_custom_f_url(self):
        files = Storage('files')
        self.configure(files,
            FS_URL='http://somewhere.net/test/',
            FILES_FS_URL='http://somewhere-else.net/test/'
        )
        with self.app.test_request_context():
            self.assertEqual(files.base_url, 'http://somewhere-else.net/test/')
