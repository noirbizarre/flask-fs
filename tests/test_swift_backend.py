# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import swiftclient

from .test_backend_mixin import BackendTestCase

from flask_fs.backends.swift import SwiftBackend
from flask_fs.storage import Config

import pytest

USER = 'test:tester'
KEY = 'testing'
AUTHURL = 'http://127.0.0.1:8080/auth/v1.0'


class SwiftBackendTest(BackendTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
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

        yield

        try:
            headers, items = self.conn.get_container(self.backend.name)
            for i in items:
                self.conn.delete_object(self.backend.name, i['name'])

            self.conn.delete_container(self.backend.name)
        except swiftclient.ClientException as e:
            assert False, "Failed to delete container ->" + str(e)

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
