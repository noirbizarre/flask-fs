# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import swiftclient

from . import TestCase
from .test_backend_mixin import BackendTestMixin

from flask_fs.backends.swift import SwiftBackend
from flask_fs.storage import Config

USER = 'test:tester'
KEY = 'testing'
AUTHURL = 'http://127.0.0.1:8080/auth/v1.0'


class SwiftBackendTest(BackendTestMixin, TestCase):
    def setUp(self):
        super(SwiftBackendTest, self).setUp()

        self.conn = swiftclient.Connection(
            user=USER,
            key=KEY,
            authurl=AUTHURL,
        )
        self.container = 'test'

        self.config = Config({
            'user': USER,
            'key': KEY,
            'authurl': AUTHURL,
        })
        self.backend = SwiftBackend(self.container, self.config)

    def tearDown(self):
        try:
            self.conn.delete_container(self.backend.name)
        except swiftclient.ClientException as e:
            print(e)

    def put_file(self, filename, content):
        self.conn.put_object(self.container, filename, contents=content)

    def get_file(self, filename):
        _, data = self.conn.get_object(self.container, filename)
        return data

    def file_exists(self, filename):
        try:
            self.conn.head_object(self.container, filename)
            return True
        except swiftclient.ClientException:
            return False
