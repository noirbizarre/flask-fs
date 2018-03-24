# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import logging

from contextlib import contextmanager
from dateutil import parser

import swiftclient

from . import BaseBackend

log = logging.getLogger(__name__)


class SwiftBackend(BaseBackend):
    '''
    An OpenStack Swift backend

    Expect the following settings:

    - `authurl`: The Swift Auth URL
    - `user`: The Swift user in
    - `key`: The user API Key
    '''
    def __init__(self, name, config):
        super(SwiftBackend, self).__init__(name, config)

        self.conn = swiftclient.Connection(
            user=config.user,
            key=config.key,
            authurl=config.authurl
        )
        self.conn.put_container(self.name)

    def exists(self, filename):
        try:
            self.conn.head_object(self.name, filename)
            return True
        except swiftclient.ClientException:
            return False

    @contextmanager
    def open(self, filename, mode='r', encoding='utf8'):
        if 'r' in mode:
            obj = self.read(filename)
            yield io.BytesIO(obj) if 'b' in mode else io.StringIO(obj.decode(encoding))
        else:  # mode == 'w'
            f = io.BytesIO() if 'b' in mode else io.StringIO()
            yield f
            self.write(filename, f.getvalue())

    def read(self, filename):
        _, data = self.conn.get_object(self.name, filename)
        return data

    def write(self, filename, content):
        self.conn.put_object(self.name, filename, contents=content)

    def delete(self, filename):
        if self.exists(filename):
            self.conn.delete_object(self.name, filename)
        else:
            headers, items = self.conn.get_container(self.name, path=filename)
            for i in items:
                self.conn.delete_object(self.name, i['name'])

    def copy(self, filename, target):
        dest = '/'.join((self.name, target))
        self.conn.copy_object(self.name, filename, destination=dest)

    def list_files(self):
        headers, items = self.conn.get_container(self.name)
        for i in items:
            yield i['name']

    def get_metadata(self, filename):
        data = self.conn.head_object(self.name, filename)
        return {
            'checksum': 'md5:{0}'.format(data['etag']),
            'size': int(data['content-length']),
            'mime': data['content-type'],
            'modified': parser.parse(data['last-modified']),
        }
