# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

from . import fake


class BackendTestMixin(object):

    def put_file(self, filename, content):
        raise NotImplementedError('You must implement this method')

    def get_file(self, filename):
        raise NotImplementedError('You must implement this method')

    def file_exists(self, filename):
        raise NotImplementedError('You must implement this method')

    def assert_bin_equal(self, filename, expected):
        data = self.get_file(filename)
        self.assertEqual(data, self.b(expected))

    def assert_text_equal(self, filename, expected):
        data = self.get_file(filename)
        self.assertEqual(data, six.b(expected))

    def test_exists(self):
        self.put_file('file.test', 'test')
        self.assertTrue(self.backend.exists('file.test'))
        self.assertFalse(self.backend.exists('other.test'))

    def test_open_read(self):
        content = self.text()
        self.put_file('file.test', content)

        with self.backend.open('file.test') as f:
            data = f.read()
            self.assertIsInstance(data, six.text_type)
            self.assertEqual(data, content)

    def test_open_read_binary(self):
        content = self.binary()
        self.put_file('file.test', content)

        with self.backend.open('file.test', 'rb') as f:
            data = f.read()
            self.assertIsInstance(data, six.binary_type)
            self.assertEqual(data, content)

    def test_open_write_new_file(self):
        filename = 'test.text'
        content = self.text()

        with self.backend.open(filename, 'w') as f:
            f.write(content)

        self.assert_text_equal(filename, content)

    def test_open_write_new_binary_file(self):
        filename = 'test.bin'
        content = self.binary()

        with self.backend.open(filename, 'wb') as f:
            f.write(content)

        self.assert_bin_equal(filename, content)

    def test_open_write_existing_file(self):
        filename = 'test.txt'
        content = self.text()
        self.put_file(filename, self.text())

        with self.backend.open(filename, 'w') as f:
            f.write(content)

        self.assert_text_equal(filename, content)

    def test_read(self):
        content = self.text()
        self.put_file('file.test', content)

        self.assertEqual(self.backend.read('file.test'), six.b(content))

    def test_write_text(self):
        content = self.text()
        self.backend.write('test.txt', content)

        self.assert_text_equal('test.txt', content)

    def test_write_binary(self):
        content = self.binary()
        self.backend.write('test.bin', content)

        self.assert_bin_equal('test.bin', content)

    def test_write_file(self):
        content = self.binary()
        self.backend.write('test.bin', self.file(content))

        self.assert_bin_equal('test.bin', content)

    def test_delete(self):
        content = fake.sentence()
        self.put_file('file.test', content)

        self.backend.delete('file.test')

        self.assertFalse(self.file_exists('file.test'))

    def test_save_content(self):
        content = self.text()
        storage = self.filestorage('test.txt', content)
        self.backend.save(storage, 'test.txt')

        self.assert_text_equal('test.txt', content)

    def test_save_from_file(self):
        content = self.binary()
        f = self.file(content)
        self.backend.save(f, 'test.png')

        f.seek(0)

        self.assert_bin_equal('test.png', content)

    def test_save_with_filename(self):
        filename = 'somewhere/test.test'
        content = self.text()
        storage = self.filestorage('test.txt', content)
        self.backend.save(storage, filename)

        self.assert_text_equal(filename, content)
