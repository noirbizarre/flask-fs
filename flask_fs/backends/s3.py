# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import io
import logging

from contextlib import contextmanager

import boto3

from botocore.exceptions import ClientError

from . import BaseBackend


log = logging.getLogger(__name__)


class S3Backend(BaseBackend):
    '''
    An Amazon S3 Backend (compatible with any S3-like API)

    Expect the following settings:

    - `endpoint`: The S3 API endpoint
    - `region`: The region to work on.
    - `access_key`: The AWS credential access key
    - `secret_key`: The AWS credential secret key
    '''
    def __init__(self, name, config):
        super(S3Backend, self).__init__(name, config)

        self.session = boto3.session.Session()
        self.s3config = boto3.session.Config(signature_version='s3v4')

        self.s3 = self.session.resource('s3',
                                        config=self.s3config,
                                        **config.s3_kwargs)
        self.bucket = self.s3.Bucket(name)

        try:
            self.bucket.load()
        except ClientError:
            self.bucket.create()

    def _convert_legacy_config(self):
        if 'endpoint' in self.config:
            self.kwargs_config.setdefault('endpoint_url', self.config.endpoint)
        if 'region' in self.config:
            self.kwargs_config.setdefault('region_name', self.config.region)
        if 'access_key' in self.config:
            self.kwargs_config.setdefault('aws_access_key_id', self.config.access_key)
        if 'secret_key' in self.config:
            self.kwargs_config.setdefault('aws_secret_access_key', self.config.secret_key)

    def exists(self, filename):
        try:
            self.bucket.Object(filename).load()
        except ClientError:
            return False
        return True

    @contextmanager
    def open(self, filename, mode='r', encoding='utf8'):
        obj = self.bucket.Object(filename)
        if 'r' in mode:
            f = obj.get()['Body']
            yield f if 'b' in mode else codecs.getreader(encoding)(f)
        else:  # mode == 'w'
            f = io.BytesIO() if 'b' in mode else io.StringIO()
            yield f
            obj.put(Body=f.getvalue())

    def read(self, filename):
        obj = self.bucket.Object(filename).get()
        return obj['Body'].read()

    def write(self, filename, content):
        return self.bucket.put_object(Key=filename, Body=self.as_binary(content))

    def delete(self, filename):
        self.bucket.Object(filename).delete()

    def list_files(self):
        for f in self.bucket.objects.all():
            yield f.key

    # def serve(self, filename):
    #     file = self.fs.get_last_version(filename)
    #     return send_file(file, mimetype=file.content_type)
