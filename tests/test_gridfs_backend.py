# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pymongo import MongoClient
from gridfs import GridFS

from . import TestCase, fake
from .test_backend_mixin import BackendTestMixin

from flask_fs.backends.gridfs import GridFsBackend
from flask_fs.storage import Config

TEST_DB = 'fstest'


class GridFsBackendTest(BackendTestMixin, TestCase):
    def setUp(self):
        super(GridFsBackendTest, self).setUp()

        self.client = MongoClient()
        self.db = self.client[TEST_DB]
        self.gfs = GridFS(self.db, 'test')

        self.config = Config({
            'mongo_url': 'mongodb://localhost:27017',
            'mongo_db': TEST_DB,
        })
        self.backend = GridFsBackend('test', self.config)

    def tearDown(self):
        self.client.drop_database(TEST_DB)

    def put_file(self, filename, content):
        self.gfs.put(content, filename=filename, encoding='utf-8')

    def get_file(self, filename):
        file = self.gfs.get_last_version(filename)
        self.assertIsNotNone(file)
        return file.read()

    def file_exists(self, filename):
        return self.gfs.exists(filename=filename)

    def test_default_bucket(self):
        backend = GridFsBackend('test_bucket', self.config)
        self.assertEqual(backend.fs._GridFS__collection.name, 'test_bucket')

    def test_config(self):
        self.assertEqual(self.backend.client.address, ('localhost', 27017))
        self.assertEqual(self.backend.db.name, TEST_DB)

    def test_delete_with_versions(self):
        filename = 'test.txt'
        self.put_file(filename, fake.sentence())
        self.put_file(filename, fake.sentence())
        self.assertEqual(self.gfs.find({'filename': filename}).count(), 2)

        self.backend.delete(filename)
        self.assertFalse(self.file_exists(filename))
