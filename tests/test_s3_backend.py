# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from . import TestCase
from .test_backend_mixin import BackendTestMixin

from flask_fs.backends.s3 import S3Backend
from flask_fs.storage import Config

import boto3

from botocore.exceptions import ClientError


# Hide over verbose boto3 logging
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)


S3_SERVER = 'http://localhost:9000'
S3_REGION = 'us-east-1'
S3_ACCESS_KEY = 'ABCDEFGHIJKLMNOQRSTU'
S3_SECRET_KEY = 'abcdefghiklmnoqrstuvwxyz1234567890abcdef'


class S3BackendTest(BackendTestMixin, TestCase):
    def setUp(self):
        super(S3BackendTest, self).setUp()

        self.session = boto3.session.Session()
        self.config = boto3.session.Config(signature_version='s3v4')

        self.s3 = self.session.resource('s3',
                                        config=self.config,
                                        endpoint_url=S3_SERVER,
                                        region_name=S3_REGION,
                                        aws_access_key_id=S3_ACCESS_KEY,
                                        aws_secret_access_key=S3_SECRET_KEY)
        self.bucket = self.s3.Bucket('test')

        self.config = Config(
            endpoint=S3_SERVER,
            region=S3_REGION,
            access_key=S3_ACCESS_KEY,
            secret_key=S3_SECRET_KEY
        )
        self.backend = S3Backend('test', self.config)

    def tearDown(self):
        for obj in self.bucket.objects.all():
            obj.delete()
        self.bucket.delete()

    def put_file(self, filename, content):
        self.bucket.put_object(Key=filename, Body=content)

    def get_file(self, filename):
        obj = self.bucket.Object(filename).get()
        return obj['Body'].read()

    def file_exists(self, filename):
        try:
            self.bucket.Object('file.test').load()
            return True
        except ClientError:
            return False

    # def test_root(self):
    #     self.assertEqual(self.backend.root, self.test_dir)

    # def test_default_root(self):
    #     self.app.config['FS_ROOT'] = self.test_dir
    #     root = self.filename('default')
    #     backend = LocalBackend('default', Config({}))
    #     with self.app.app_context():
    #         self.assertEqual(backend.root, root)
