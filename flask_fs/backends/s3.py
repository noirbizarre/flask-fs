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
                                        endpoint_url=config.endpoint,
                                        region_name=config.region,
                                        aws_access_key_id=config.access_key,
                                        aws_secret_access_key=config.secret_key)
        self.bucket = self.s3.Bucket(name)

        if self.bucket.creation_date is None:
            # Boto3 does not automatically get the region from the conneciton information
            # They use the default US Standard region.
            # Ref: https://github.com/boto/boto3/issues/781
            self.bucket.create(CreateBucketConfiguration={
                'LocationConstraint': self.s3.meta.client.meta.region_name
            })

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
        for obj in self.bucket.objects.filter(Prefix=filename):
            obj.delete()

    def copy(self, filename, target):
        src = {
            'Bucket': self.bucket.name,
            'Key': filename,
        }
        self.bucket.copy(src, target)

    def list_files(self):
        for f in self.bucket.objects.all():
            yield f.key

    def get_metadata(self, filename):
        '''Fetch all availabe metadata'''
        obj = self.bucket.Object(filename)
        checksum = 'md5:{0}'.format(obj.e_tag[1:-1])
        mime = obj.content_type.split(';', 1)[0] if obj.content_type else None
        return {
            'checksum': checksum,
            'size': obj.content_length,
            'mime': mime,
            'modified': obj.last_modified,
        }

    # def serve(self, filename):
    #     file = self.fs.get_last_version(filename)
    #     return send_file(file, mimetype=file.content_type)
