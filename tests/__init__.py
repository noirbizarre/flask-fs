# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import os
import unittest
import six

from flask import Flask
from faker import Faker
from werkzeug.datastructures import FileStorage

BIN_FILE = os.path.join(os.path.dirname(__file__), 'flask.png')

fake = Faker()


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def configure(self, *storages, **configs):
        import flask_fs as fs
        for key, value in configs.items():
            self.app.config[key] = value
        fs.init_app(self.app, *storages)

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
        return six.text_type(fake.sentence())

    def binary(self):
        return six.binary_type(fake.binary())
