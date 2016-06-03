# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import mock

from flask import url_for

from . import TestCase, fake

import flask_fs as fs


class MockBackend(fs.BaseBackend):
    pass


# The mock backend fully qualitfied class name
MOCK_BACKEND = '.'.join((__name__, MockBackend.__name__))


def mock_backend(func):
    return mock.patch(MOCK_BACKEND)(func)


class StorageTestCase(TestCase):
    def configure(self, *storages, **configs):
        self.app.config['FS_BACKEND'] = configs.pop('FS_BACKEND', MOCK_BACKEND)
        super(StorageTestCase, self).configure(*storages, **configs)

    @mock_backend
    def test_by_name(self, mock_backend):
        storage = fs.Storage('test_storage')
        self.configure(storage)

        with self.app.app_context():
            self.assertEqual(fs.by_name('test_storage'), storage)

    @mock_backend
    def test_exists(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value

        with self.app.app_context():
            backend.exists.return_value = True
            self.assertTrue(storage.exists('file.test'))
            backend.exists.assert_called_with('file.test')

            backend.exists.return_value = False
            self.assertFalse(storage.exists('other.test'))

    @mock_backend
    def test_in_operator(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value

        with self.app.app_context():
            backend.exists.return_value = True
            self.assertTrue('file.test' in storage)
            self.assertIn('file.test', storage)
            self.assertEqual(backend.exists.call_count, 2)
            backend.exists.assert_called_with('file.test')

            backend.exists.reset_mock()
            backend.exists.return_value = False
            self.assertFalse('other.test' in storage)
            self.assertNotIn('other.test', storage)
            self.assertEqual(backend.exists.call_count, 2)
            backend.exists.assert_called_with('other.test')

    @mock_backend
    def test_open(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.open.return_value = io.StringIO('content')

        with storage.open('file.test') as f:
            self.assertEqual(f.read(), 'content')

        backend.open.assert_called_with('file.test', 'r')

    @mock_backend
    def test_open_write_new_file(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.open.return_value = io.StringIO('content')

        with storage.open('file.test', 'w') as f:
            f.write('test')
            # self.assertEqual(f.read(), 'content')

        backend.open.assert_called_with('file.test', 'w')

    @mock_backend
    def test_open_read_not_found(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.assertRaises(fs.FileNotFound):
            with storage.open('file.test'):
                pass

    @mock_backend
    def test_read(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.read.return_value = 'content'

        with self.app.app_context():
            self.assertEqual(storage.read('file.test'), 'content')

    @mock_backend
    def test_read_not_found(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context(), self.assertRaises(fs.FileNotFound):
            storage.read('file.test')

    @mock_backend
    def test_write(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            storage.write('file.test', 'content')
            backend.exists.assert_called_with('file.test')
            backend.write.assert_called_with('file.test', 'content')

    @mock_backend
    def test_write_file_exists(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = True

        with self.app.app_context():
            with self.assertRaises(fs.FileExists):
                storage.write('file.test', 'content')

    @mock_backend
    def test_write_overwrite(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        backend = mock_backend.return_value

        with self.app.app_context():
            storage.write('file.test', 'content', overwrite=True)

        backend.write.assert_called_with('file.test', 'content')

    @mock_backend
    def test_write_overwritable(self, mock_backend):
        storage = fs.Storage('test', overwrite=True)
        self.configure(storage)

        backend = mock_backend.return_value

        with self.app.app_context():
            storage.write('file.test', 'content')

        backend.write.assert_called_with('file.test', 'content')

    @mock_backend
    def test_save_file_exists(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        f = self.file(fake.binary())

        backend = mock_backend.return_value
        backend.exists.return_value = True

        with self.app.app_context():
            with self.assertRaises(fs.FileExists):
                storage.save(f, 'test.png')

    @mock_backend
    def test_save_overwrite(self, mock_backend):
        storage = fs.Storage('test')
        self.configure(storage)

        f = self.file(fake.binary())

        backend = mock_backend.return_value
        backend.exists.return_value = True

        with self.app.app_context():
            filename = storage.save(f, 'test.png', overwrite=True)

        self.assertEqual(filename, 'test.png')
        backend.save.assert_called_with(f, 'test.png')

    @mock_backend
    def test_save_from_file(self, mock_backend):
        storage = fs.Storage('test')
        f = self.file(fake.binary())

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(f, 'test.png')

        self.assertEqual(filename, 'test.png')
        backend.save.assert_called_with(f, 'test.png')

    @mock_backend
    def test_save_from_file_storage(self, mock_backend):
        storage = fs.Storage('test')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs)

        self.assertEqual(filename, 'test.txt')
        backend.save.assert_called_with(wfs, 'test.txt')

    @mock_backend
    def test_save_with_filename(self, mock_backend):
        storage = fs.Storage('test')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs, 'other.gif')

        self.assertEqual(filename, 'other.gif')
        backend.save.assert_called_with(wfs, 'other.gif')

    @mock_backend
    def test_save_with_prefix(self, mock_backend):
        storage = fs.Storage('test')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs, prefix='prefix')

        self.assertEqual(filename, 'prefix/test.txt')
        backend.save.assert_called_with(wfs, 'prefix/test.txt')

    @mock_backend
    def test_save_with_callable_prefix(self, mock_backend):
        storage = fs.Storage('test')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs, prefix=lambda: 'prefix')

        self.assertEqual(filename, 'prefix/test.txt')
        backend.save.assert_called_with(wfs, 'prefix/test.txt')

    @mock_backend
    def test_save_with_upload_to(self, mock_backend):
        storage = fs.Storage('test', upload_to='upload_to')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs)

        self.assertEqual(filename, 'upload_to/test.txt')
        backend.save.assert_called_with(wfs, 'upload_to/test.txt')

    @mock_backend
    def test_save_with_callable_upload_to(self, mock_backend):
        storage = fs.Storage('test', upload_to=lambda: 'upload_to')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs)

        self.assertEqual(filename, 'upload_to/test.txt')
        backend.save.assert_called_with(wfs, 'upload_to/test.txt')

    @mock_backend
    def test_save_with_upload_to_and_prefix(self, mock_backend):
        storage = fs.Storage('test', upload_to='upload_to')
        content = 'test'
        wfs = self.filestorage('test.txt', content)

        self.configure(storage)

        backend = mock_backend.return_value
        backend.exists.return_value = False

        with self.app.app_context():
            filename = storage.save(wfs, prefix='prefix')

        self.assertEqual(filename, 'upload_to/prefix/test.txt')
        backend.save.assert_called_with(wfs, 'upload_to/prefix/test.txt')

    @mock_backend
    def test_delete(self, mock_backend):
        storage = fs.Storage('test')

        self.configure(storage)

        backend = mock_backend.return_value

        with self.app.app_context():
            storage.delete('test.txt')

        backend.delete.assert_called_with('test.txt')

    def test_url(self):
        storage = fs.Storage('test')

        self.configure(storage)

        with self.app.test_request_context():
            params = {'fs': storage.name, 'filename': 'test.txt'}
            expected_url = url_for('fs.get_file', **params)
            self.assertEqual(storage.url('test.txt'), expected_url)

            params['_external'] = True
            expected_url = url_for('fs.get_file', **params)
            self.assertEqual(storage.url('test.txt', external=True), expected_url)

    def test_url_from_config_without_scheme(self):
        storage = fs.Storage('test')

        self.configure(storage, TEST_FS_URL='somewhere.com/static')

        with self.app.test_request_context():
            self.assertEqual(storage.url('test.txt'), 'http://somewhere.com/static/test.txt')

        with self.app.test_request_context(environ_overrides={'wsgi.url_scheme': 'http'}):
            self.assertEqual(storage.url('test.txt'), 'http://somewhere.com/static/test.txt')

        with self.app.test_request_context(environ_overrides={'wsgi.url_scheme': 'https'}):
            self.assertEqual(storage.url('test.txt'), 'https://somewhere.com/static/test.txt')

    def test_url_from_config_with_scheme(self):
        http = fs.Storage('http')
        https = fs.Storage('https')

        self.configure(http, https,
            HTTP_FS_URL='http://somewhere.com/static',
            HTTPS_FS_URL='https://somewhere.com/static'
        )

        with self.app.app_context():
            self.assertEqual(http.url('test.txt'), 'http://somewhere.com/static/test.txt')
            self.assertEqual(https.url('test.txt'), 'https://somewhere.com/static/test.txt')

        with self.app.test_request_context(environ_overrides={'wsgi.url_scheme': 'http'}):
            self.assertEqual(http.url('test.txt'), 'http://somewhere.com/static/test.txt')
            self.assertEqual(https.url('test.txt'), 'https://somewhere.com/static/test.txt')

        with self.app.test_request_context(environ_overrides={'wsgi.url_scheme': 'https'}):
            self.assertEqual(http.url('test.txt'), 'http://somewhere.com/static/test.txt')
            self.assertEqual(https.url('test.txt'), 'https://somewhere.com/static/test.txt')

    @mock_backend
    def test_root(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.root = '/root'

        self.configure(storage, SERVER_NAME='somewhere')

        with self.app.app_context():
            self.assertEqual(storage.root, '/root')

    @mock_backend
    def test_no_root(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.root = None

        self.configure(storage, SERVER_NAME='somewhere')

        with self.app.app_context():
            self.assertIsNone(storage.root)

    @mock_backend
    def test_path(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.root = '/root'

        self.configure(storage)
        self.assertEqual(storage.path('file.test'), '/root/file.test')

    @mock_backend
    def test_path_not_supported(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.root = None

        self.configure(storage)

        with self.assertRaises(fs.OperationNotSupported):
            storage.path('file.test')

    # @mock_backend
    # def test_serve(self, mock_backend):
    #     storage = fs.Storage('test')
    #     backend = mock_backend.return_value
    #     # backend.root = '/root'
    #
    #     self.configure(storage)
    #     self.assertEqual(storage.path('file.test'), '/root/file.test')

    # def test_path(self):
    #     expected = join(self.test_dir, 'file.test')
    #     self.assertEqual(self.backend.path('file.test'), expected)

    # def test_delete(self):
    #     with open(join(self.test_dir, 'file.test'), 'w') as f:
    #         f.write('test')

    #     self.backend.delete('file.test')

    #     self.assertFalse(exists(join(self.test_dir, 'file.test')))

    # def test_path(self):
    #     expected = join(self.test_dir, 'file.test')
    #     self.assertEqual(self.backend.path('file.test'), expected)

    # def test_save(self):
    #     content = 'test'
    #     storage = filestorage('test.txt', content)
    #     self.backend.save(storage, 'test.txt')

    #     with open(join(self.test_dir, 'test.txt'), 'r') as f:
    #         self.assertEqual(f.read(), content)

    # def test_save_with_filename(self):
    #     content = 'test'
    #     storage = filestorage('test.txt', content)
    #     self.backend.save(storage, 'somewhere/test.test')

    #     with open(join(self.test_dir, 'somewhere/test.test'), 'r') as f:
    #         self.assertEqual(f.read(), content)

    # def test_save_deny_overwrite(self):
    #     filename = 'file.test'
    #     with open(join(self.test_dir, filename), 'w') as f:
    #         f.write('initial')

    #     content = 'test'
    #     storage = filestorage('whatever', content)
    #     with self.assertRaises(FileExists):
    #         self.backend.save(storage, filename)

    # def test_save_allow_overwrite(self):
    #     filename = 'file.test'
    #     with open(join(self.test_dir, filename), 'w') as f:
    #         f.write('initial')

    #     content = 'test'
    #     storage = filestorage('whatever', content)
    #     self.backend.save(storage, filename, overwrite=True)

    #     with open(join(self.test_dir, 'file.test'), 'r') as f:
    #         self.assertEqual(f.read(), content)
