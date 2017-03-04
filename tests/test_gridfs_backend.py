# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pymongo import MongoClient
from gridfs import GridFS

from .test_backend_mixin import BackendTestCase

from flask_fs.backends.gridfs import GridFsBackend
from flask_fs.storage import Config

import pytest

TEST_DB = 'fstest'


class GridFsBackendTest(BackendTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = MongoClient()
        self.db = self.client[TEST_DB]
        self.gfs = GridFS(self.db, 'test')

        self.config = Config({
            'mongo_url': 'mongodb://localhost:27017',
            'mongo_db': TEST_DB,
        })
        self.backend = GridFsBackend('test', self.config)
        yield
        self.client.drop_database(TEST_DB)

    def put_file(self, filename, content):
        self.gfs.put(content, filename=filename, encoding='utf-8')

    def get_file(self, filename):
        file = self.gfs.get_last_version(filename)
        assert file is not None
        return file.read()

    def file_exists(self, filename):
        return self.gfs.exists(filename=filename)

    def test_default_bucket(self):
        backend = GridFsBackend('test_bucket', self.config)
        assert backend.fs._GridFS__collection.name == 'test_bucket'

    def test_config(self):
        assert self.backend.client.address == ('localhost', 27017)
        assert self.backend.db.name == TEST_DB

    def test_delete_with_versions(self, faker):
        filename = 'test.txt'
        self.put_file(filename, faker.sentence())
        self.put_file(filename, faker.sentence())
        assert self.gfs.find({'filename': filename}).count() == 2

        self.backend.delete(filename)
        assert not self.file_exists(filename)
