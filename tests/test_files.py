# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask_fs import files

from . import TestCase


class TestFiles(TestCase):
    def test_extension(self):
        self.assertEqual(files.extension('foo.txt'), 'txt')
        self.assertEqual(files.extension('foo'), '')
        self.assertEqual(files.extension('archive.tar.gz'), 'gz')
        self.assertEqual(files.extension('audio.m4a'), 'm4a')

    def test_lowercase_ext(self):
        self.assertEqual(files.lower_extension('foo.txt'), 'foo.txt')
        self.assertEqual(files.lower_extension('FOO.TXT'), 'FOO.txt')
        self.assertEqual(files.lower_extension('foo'), 'foo')
        self.assertEqual(files.lower_extension('FOO'), 'FOO')
        self.assertEqual(files.lower_extension('archive.tar.gz'), 'archive.tar.gz')
        self.assertEqual(files.lower_extension('ARCHIVE.TAR.GZ'), 'ARCHIVE.TAR.gz')
        self.assertEqual(files.lower_extension('audio.m4a'), 'audio.m4a')
        self.assertEqual(files.lower_extension('AUDIO.M4A'), 'AUDIO.m4a')

    def test_ALL(self):
        self.assertIn('txt', files.ALL)
        self.assertIn('exe', files.ALL)

    def test_all_except(self):
        all_except = files.AllExcept('exe')
        self.assertIn('csv', all_except)
        self.assertNotIn('exe', all_except)
